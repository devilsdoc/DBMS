"""
HoD and Class Teacher Reporting APIs: Aggregated Division Attendance, Course Trends, and Defaulters
"""

import io
import csv
from datetime import date
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models import (
    Division, ClassEntity, Teacher, ClassTeacherAllocation,
    Student, Course, Attendance, AcademicSession
)
from backend.schemas import DivisionReportResponse
from backend.dependencies import role_checker, AuthenticatedUser

router = APIRouter(tags=["Reports & Analytics"])

@router.get("/reports/division/{div_id}", response_model=DivisionReportResponse)
@router.get("/api/v1/reports/division/{div_id}", response_model=DivisionReportResponse)
def get_division_report(
    div_id: str,
    current_user: AuthenticatedUser = Depends(role_checker(["HOD", "CLASS_TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    CRITICAL ACCESS RULE:
    - HoD (EMP001): Unrestricted access to any division in the CSE department.
    - Class Teacher (EMP002 for DIV01, EMP003 for DIV02, EMP004 for DIV03):
      STRICTLY restricted to their assigned division. Cross-division access is denied with 403.
    """
    clean_div_id = div_id.strip()

    # RBAC Class Teacher Boundary Check
    if not current_user.is_hod():
        ct_alloc = db.query(ClassTeacherAllocation).filter(
            ClassTeacherAllocation.emp_id == current_user.user_id,
            ClassTeacherAllocation.div_id == clean_div_id,
            ClassTeacherAllocation.is_active == True
        ).first()

        if not ct_alloc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Security Violation: You are not the assigned Class Teacher for division '{clean_div_id}'."
            )

    # 1. Fetch Division Information
    division = db.query(Division).filter(Division.div_id == clean_div_id).first()
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Division '{clean_div_id}' not found.")

    class_info = db.query(ClassEntity).filter(ClassEntity.class_id == division.class_id).first()
    class_name = class_info.class_name if class_info else "CSE Class"

    # Fetch assigned Class Teacher
    ct_assignment = db.query(ClassTeacherAllocation).filter(
        ClassTeacherAllocation.div_id == clean_div_id,
        ClassTeacherAllocation.is_active == True
    ).first()
    ct_name = None
    if ct_assignment:
        ct_teacher = db.query(Teacher).filter(Teacher.emp_id == ct_assignment.emp_id).first()
        ct_name = ct_teacher.teacher_name if ct_teacher else ct_assignment.emp_id

    # 2. Fetch all students in this division
    students = db.query(Student).filter(Student.div_id == clean_div_id, Student.status == 'Active').all()
    total_students = len(students)
    student_ids = [s.student_id for s in students]

    # Total sessions conducted for this division
    total_sessions = (
        db.query(func.count(AcademicSession.session_id))
        .filter(
            AcademicSession.div_id == clean_div_id,
            AcademicSession.session_status == 'Conducted'
        )
        .scalar() or 0
    )

    # 3. Compute student attendance & identify defaulters (<75%)
    defaulters = []
    total_division_pct_sum = 0.0

    for s in students:
        total_st_sessions = (
            db.query(func.count(Attendance.attendance_id))
            .filter(Attendance.student_id == s.student_id)
            .scalar() or 0
        )
        attended_st_sessions = (
            db.query(func.count(Attendance.attendance_id))
            .filter(
                Attendance.student_id == s.student_id,
                Attendance.status.in_(["Present", "Late"])
            )
            .scalar() or 0
        )

        pct = round((attended_st_sessions / total_st_sessions * 100), 2) if total_st_sessions > 0 else 0.0
        total_division_pct_sum += pct

        if pct < 75.0:
            defaulters.append({
                "student_id": s.student_id,
                "roll_no": s.roll_no,
                "student_name": s.student_name,
                "total_conducted": total_st_sessions,
                "total_attended": attended_st_sessions,
                "attendance_percentage": pct,
                "email": s.email,
                "phone": s.phone
            })

    div_avg_pct = round(total_division_pct_sum / total_students, 2) if total_students > 0 else 0.0

    # 4. Course-wise attendance stats for this division
    course_query = (
        db.query(
            Course.course_id,
            Course.course_code,
            Course.course_name,
            Attendance.status
        )
        .join(Attendance, Course.course_id == Attendance.course_id)
        .filter(Attendance.student_id.in_(student_ids))
        .all()
    )

    course_stats_map = {}
    for cq in course_query:
        cid = cq.course_id
        if cid not in course_stats_map:
            course_stats_map[cid] = {
                "course_id": cid,
                "course_code": cq.course_code,
                "course_name": cq.course_name,
                "total_records": 0,
                "attended_records": 0
            }
        course_stats_map[cid]["total_records"] += 1
        if cq.status in ["Present", "Late"]:
            course_stats_map[cid]["attended_records"] += 1

    course_statistics = []
    for cid, data in sorted(course_stats_map.items()):
        c_pct = round(data["attended_records"] / data["total_records"] * 100, 2) if data["total_records"] > 0 else 0.0
        course_statistics.append({
            "course_id": cid,
            "course_code": data["course_code"],
            "course_name": data["course_name"],
            "average_percentage": c_pct
        })

    return DivisionReportResponse(
        div_id=clean_div_id,
        div_name=division.div_name,
        class_name=class_name,
        class_teacher_name=ct_name,
        total_students=total_students,
        total_sessions_conducted=total_sessions,
        division_average_percentage=div_avg_pct,
        defaulters_count=len(defaulters),
        defaulters=sorted(defaulters, key=lambda x: x["attendance_percentage"]),
        course_statistics=course_statistics
    )

@router.get("/reports/division/{div_id}/export-csv")
@router.get("/api/v1/reports/division/{div_id}/export-csv")
def export_division_attendance_csv(
    div_id: str,
    current_user: AuthenticatedUser = Depends(role_checker(["HOD", "CLASS_TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Exports a comprehensive CSV report of all students in the division,
    including total sessions, attended sessions, percentage, and defaulter status (<75%).
    """
    clean_div_id = div_id.strip()

    # RBAC Class Teacher Boundary Check
    if not current_user.is_hod():
        ct_alloc = db.query(ClassTeacherAllocation).filter(
            ClassTeacherAllocation.emp_id == current_user.user_id,
            ClassTeacherAllocation.div_id == clean_div_id,
            ClassTeacherAllocation.is_active == True
        ).first()

        if not ct_alloc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Security Violation: You are not the assigned Class Teacher for division '{clean_div_id}'."
            )

    division = db.query(Division).filter(Division.div_id == clean_div_id).first()
    if not division:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Division '{clean_div_id}' not found.")

    students = db.query(Student).filter(Student.div_id == clean_div_id, Student.status == 'Active').order_by(Student.roll_no).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow([
        "Roll_No",
        "Student_ID",
        "Student_Name",
        "Division",
        "Total_Sessions_Conducted",
        "Total_Sessions_Attended",
        "Attendance_Percentage",
        "Defaulter_Status",
        "Parent_Intimation_Required",
        "Email",
        "Phone"
    ])

    for s in students:
        total = db.query(func.count(Attendance.attendance_id)).filter(Attendance.student_id == s.student_id).scalar() or 0
        attended = db.query(func.count(Attendance.attendance_id)).filter(
            Attendance.student_id == s.student_id,
            Attendance.status.in_(["Present", "Late"])
        ).scalar() or 0
        pct = round((attended / total * 100), 2) if total > 0 else 0.0
        is_def = "DEFAULTER (< 75%)" if pct < 75.0 else "GOOD STANDING"
        parent_notice = "YES" if pct < 75.0 else "NO"

        writer.writerow([
            s.roll_no,
            s.student_id,
            s.student_name,
            division.div_name,
            total,
            attended,
            f"{pct}%",
            is_def,
            parent_notice,
            s.email,
            s.phone
        ])

    csv_data = output.getvalue()
    filename = f"Attendance_Report_{division.div_name}_{date.today().strftime('%Y%m%d')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

