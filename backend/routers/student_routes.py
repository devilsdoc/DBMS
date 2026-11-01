"""
Student APIs: Personal Attendance Dashboard and Defaulter Warnings
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import Student, Division, Course, Attendance
from backend.schemas import StudentAttendanceDashboard, SubjectAttendanceDetail
from backend.dependencies import role_checker, AuthenticatedUser

router = APIRouter(tags=["Student"])

@router.get("/student/my-attendance", response_model=StudentAttendanceDashboard)
@router.get("/api/v1/student/my-attendance", response_model=StudentAttendanceDashboard)
def get_my_attendance(
    current_user: AuthenticatedUser = Depends(role_checker(["STUDENT"])),
    db: Session = Depends(get_db)
):
    """
    CRITICAL ACCESS RULE:
    Returns overall attendance and subject-wise breakdown STRICTLY for the logged-in student.
    A student cannot specify or query any other student's identifier.
    """
    student_id = current_user.user_id

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    div = db.query(Division).filter(Division.div_id == student.div_id).first()
    div_name = div.div_name if div else student.div_id

    # Fetch all attendance records for this student
    records = (
        db.query(
            Attendance.attendance_id,
            Attendance.course_id,
            Course.course_code,
            Course.course_name,
            Attendance.attendance_date,
            Attendance.slot_no,
            Attendance.status
        )
        .join(Course, Attendance.course_id == Course.course_id)
        .filter(Attendance.student_id == student_id)
        .order_by(Attendance.attendance_date.desc(), Attendance.slot_no.desc())
        .all()
    )

    total_conducted = len(records)
    total_attended = sum(1 for r in records if r.status in ["Present", "Late"])
    overall_pct = round((total_attended / total_conducted * 100), 2) if total_conducted > 0 else 0.0
    is_defaulter = overall_pct < 75.0

    # Course-wise breakdown
    course_map = {}
    absent_dates = []

    for r in records:
        cid = r.course_id
        if cid not in course_map:
            course_map[cid] = {
                "code": r.course_code,
                "name": r.course_name,
                "conducted": 0,
                "attended": 0
            }
        course_map[cid]["conducted"] += 1
        if r.status in ["Present", "Late"]:
            course_map[cid]["attended"] += 1
        elif r.status == "Absent":
            absent_dates.append({
                "date": str(r.attendance_date),
                "slot_no": r.slot_no,
                "course_code": r.course_code,
                "course_name": r.course_name
            })

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

    return StudentAttendanceDashboard(
        student_id=student.student_id,
        student_name=student.student_name,
        roll_no=student.roll_no,
        div_id=student.div_id,
        div_name=div_name,
        total_conducted=total_conducted,
        total_attended=total_attended,
        overall_percentage=overall_pct,
        is_defaulter=is_defaulter,
        courses=subject_breakdown,
        absent_dates=absent_dates
    )
