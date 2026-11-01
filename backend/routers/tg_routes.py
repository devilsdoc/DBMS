"""
Teacher Guardian (TG) APIs: Strict 20-Student Mentorship Boundary & Cross-Course Defaulter Reports
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import (
    TeacherGuardian, TGStudentAllocation, Student, Division,
    Course, Attendance, AcademicSession, DefaulterAlert
)
from backend.schemas import (
    TGStudentInfo, TGStudentAttendanceReport, SubjectAttendanceDetail
)
from backend.dependencies import role_checker, AuthenticatedUser

router = APIRouter(tags=["Teacher Guardian (TG)"])

@router.get("/tg/my-students", response_model=List[TGStudentInfo])
@router.get("/api/v1/tg/my-students", response_model=List[TGStudentInfo])
def get_my_tg_students(
    current_user: AuthenticatedUser = Depends(role_checker(["TEACHER_GUARDIAN"])),
    db: Session = Depends(get_db)
):
    """
    CRITICAL ACCESS RULE:
    Fetches ONLY the students explicitly allocated to this logged-in TG in TG_Student_Allocation.
    No TG can view students belonging to other mentor groups.
    """
    query = (
        db.query(
            Student.student_id,
            Student.roll_no,
            Student.student_name,
            Student.div_id,
            Division.div_name,
            Student.email,
            Student.phone
        )
        .join(TGStudentAllocation, Student.student_id == TGStudentAllocation.student_id)
        .join(Division, Student.div_id == Division.div_id)
        .filter(
            TGStudentAllocation.teacher_id == current_user.user_id,
            TGStudentAllocation.status == 'Active'
        )
        .order_by(Student.roll_no)
        .all()
    )

    if not query and not current_user.is_hod():
        return []

    return [
        TGStudentInfo(
            student_id=q.student_id,
            roll_no=q.roll_no,
            student_name=q.student_name,
            div_id=q.div_id,
            div_name=q.div_name,
            email=q.email,
            phone=q.phone
        )
        for q in query
    ]

@router.get("/tg/attendance-report", response_model=List[TGStudentAttendanceReport])
@router.get("/api/v1/tg/attendance-report", response_model=List[TGStudentAttendanceReport])
def get_tg_attendance_report(
    current_user: AuthenticatedUser = Depends(role_checker(["TEACHER_GUARDIAN"])),
    db: Session = Depends(get_db)
):
    """
    CRITICAL ACCESS RULE:
    Calculates attendance percentage of the TG's allotted 20 students across ALL courses.
    Flags students falling below 75% as defaulters and provides subject-wise breakdown.
    """
    # 1. Fetch strictly the students allotted to this TG
    allocations = (
        db.query(TGStudentAllocation.student_id)
        .filter(
            TGStudentAllocation.teacher_id == current_user.user_id,
            TGStudentAllocation.status == 'Active'
        )
        .all()
    )
    student_ids = [a.student_id for a in allocations]

    if not student_ids and not current_user.is_hod():
        return []

    # If HoD is querying, allow view of all students or default group
    if current_user.is_hod() and not student_ids:
        allocations = db.query(TGStudentAllocation.student_id).limit(20).all()
        student_ids = [a.student_id for a in allocations]

    students = db.query(Student).filter(Student.student_id.in_(student_ids)).order_by(Student.roll_no).all()

    # 2. Compute aggregate attendance for each student
    reports = []
    for s in students:
        # Total conducted and attended across all courses
        total_conducted = (
            db.query(func.count(Attendance.attendance_id))
            .filter(Attendance.student_id == s.student_id)
            .scalar() or 0
        )
        total_attended = (
            db.query(func.count(Attendance.attendance_id))
            .filter(
                Attendance.student_id == s.student_id,
                Attendance.status.in_(["Present", "Late"])
            )
            .scalar() or 0
        )

        overall_pct = round((total_attended / total_conducted * 100), 2) if total_conducted > 0 else 0.0
        is_defaulter = overall_pct < 75.0

        # Course-wise breakdown
        course_stats = (
            db.query(
                Course.course_id,
                Course.course_code,
                Course.course_name,
                func.count(Attendance.attendance_id).label("conducted"),
                func.sum(
                    case=None,
                    *[(Attendance.status.in_(["Present", "Late"])).cast(func.INTEGER if db.bind.dialect.name == "sqlite" else func.INT)]
                ) if False else func.count(Attendance.attendance_id) # Handled cleanly below
            )
        )
        # Using pure Python / portable SQLAlchemy grouping for cross-database speed:
        att_rows = (
            db.query(Attendance.course_id, Course.course_code, Course.course_name, Attendance.status)
            .join(Course, Attendance.course_id == Course.course_id)
            .filter(Attendance.student_id == s.student_id)
            .all()
        )

        course_map = {}
        for row in att_rows:
            cid = row.course_id
            if cid not in course_map:
                course_map[cid] = {
                    "code": row.course_code,
                    "name": row.course_name,
                    "conducted": 0,
                    "attended": 0
                }
            course_map[cid]["conducted"] += 1
            if row.status in ["Present", "Late"]:
                course_map[cid]["attended"] += 1

        subject_breakdown = [
            SubjectAttendanceDetail(
                course_id=cid,
                course_code=data["code"],
                course_name=data["name"],
                conducted=data["conducted"],
                attended=data["attended"],
                percentage=round((data["attended"] / data["conducted"] * 100), 2) if data["conducted"] > 0 else 0.0
            )
            for cid, data in sorted(course_map.items())
        ]

        reports.append(
            TGStudentAttendanceReport(
                student_id=s.student_id,
                roll_no=s.roll_no,
                student_name=s.student_name,
                div_id=s.div_id,
                total_conducted=total_conducted,
                total_attended=total_attended,
                attendance_percentage=overall_pct,
                is_defaulter=is_defaulter,
                subject_wise=subject_breakdown
            )
        )

    return reports

@router.get("/tg/alerts")
@router.get("/api/v1/tg/alerts")
def get_tg_alerts(
    current_user: AuthenticatedUser = Depends(role_checker(["TEACHER_GUARDIAN"])),
    db: Session = Depends(get_db)
):
    """
    Returns defaulter alerts strictly for students allocated to the logged-in TG.
    """
    allocations = (
        db.query(TGStudentAllocation.student_id)
        .filter(
            TGStudentAllocation.teacher_id == current_user.user_id,
            TGStudentAllocation.status == 'Active'
        )
        .all()
    )
    student_ids = [a.student_id for a in allocations]

    if current_user.is_hod() and not student_ids:
        alerts_query = (
            db.query(DefaulterAlert, Student.student_name, Student.roll_no)
            .join(Student, DefaulterAlert.student_id == Student.student_id)
            .order_by(DefaulterAlert.created_at.desc())
            .all()
        )
    else:
        if not student_ids:
            return {"unread_count": 0, "alerts": []}
        alerts_query = (
            db.query(DefaulterAlert, Student.student_name, Student.roll_no)
            .join(Student, DefaulterAlert.student_id == Student.student_id)
            .filter(DefaulterAlert.student_id.in_(student_ids))
            .order_by(DefaulterAlert.created_at.desc())
            .all()
        )

    unread_count = sum(1 for a, _, _ in alerts_query if not a.is_read)

    return {
        "unread_count": unread_count,
        "alerts": [
            {
                "alert_id": a.alert_id,
                "student_id": a.student_id,
                "student_name": name,
                "roll_no": roll,
                "div_id": a.div_id,
                "attendance_percentage": a.attendance_percentage,
                "alert_date": str(a.alert_date),
                "is_read": a.is_read,
                "message": a.message,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a, name, roll in alerts_query
        ]
    }

@router.patch("/tg/alerts/{alert_id}/read")
@router.patch("/api/v1/tg/alerts/{alert_id}/read")
def mark_alert_read(
    alert_id: int,
    current_user: AuthenticatedUser = Depends(role_checker(["TEACHER_GUARDIAN"])),
    db: Session = Depends(get_db)
):
    """Marks an alert notification as acknowledged/read."""
    alert = db.query(DefaulterAlert).filter(DefaulterAlert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")
    alert.is_read = True
    db.commit()
    return {"status": "SUCCESS", "message": f"Alert {alert_id} marked as read."}
