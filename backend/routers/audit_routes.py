"""
Attendance Audit Trail APIs: Modification Logs for HoD and Class Teachers
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models import (
    AttendanceAuditTrail, Attendance, Student, Teacher, Course, Division
)
from backend.dependencies import role_checker, AuthenticatedUser

router = APIRouter(tags=["Audit Trail"])

@router.get("/audit-trail")
@router.get("/api/v1/audit-trail")
def get_audit_trail_logs(
    current_user: AuthenticatedUser = Depends(role_checker(["HOD", "CLASS_TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Returns immutable audit modification logs.
    - HoD: Entire department logs.
    - Class Teacher: Logs scoped to students within their assigned division.
    """
    query = (
        db.query(
            AttendanceAuditTrail.audit_id,
            AttendanceAuditTrail.attendance_id,
            AttendanceAuditTrail.old_value,
            AttendanceAuditTrail.new_value,
            AttendanceAuditTrail.modified_by_emp_id,
            Teacher.teacher_name.label("modified_by_name"),
            AttendanceAuditTrail.modification_timestamp,
            AttendanceAuditTrail.reason,
            AttendanceAuditTrail.ip_address,
            Attendance.attendance_date,
            Attendance.slot_no,
            Student.student_id,
            Student.student_name,
            Student.roll_no,
            Student.div_id,
            Division.div_name,
            Course.course_code,
            Course.course_name
        )
        .join(Attendance, AttendanceAuditTrail.attendance_id == Attendance.attendance_id)
        .join(Teacher, AttendanceAuditTrail.modified_by_emp_id == Teacher.emp_id)
        .join(Student, Attendance.student_id == Student.student_id)
        .join(Division, Student.div_id == Division.div_id)
        .join(Course, Attendance.course_id == Course.course_id)
    )

    # If Class Teacher, scope strictly to their division
    if not current_user.is_hod():
        if not current_user.assigned_division:
            return []
        query = query.filter(Student.div_id == current_user.assigned_division)

    logs = query.order_by(desc(AttendanceAuditTrail.modification_timestamp)).all()

    return [
        {
            "audit_id": l.audit_id,
            "attendance_id": l.attendance_id,
            "old_value": l.old_value,
            "new_value": l.new_value,
            "modified_by_emp_id": l.modified_by_emp_id,
            "modified_by_name": l.modified_by_name,
            "timestamp": l.modification_timestamp.isoformat() if l.modification_timestamp else None,
            "reason": l.reason,
            "ip_address": l.ip_address,
            "attendance_date": str(l.attendance_date),
            "slot_no": l.slot_no,
            "student_id": l.student_id,
            "student_name": l.student_name,
            "roll_no": l.roll_no,
            "div_id": l.div_id,
            "div_name": l.div_name,
            "course_code": l.course_code,
            "course_name": l.course_name
        }
        for l in logs
    ]
