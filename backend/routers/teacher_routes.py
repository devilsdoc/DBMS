"""
Course Teacher APIs: Course Retrieval, Atomic Attendance Submission, and Audited Modification
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database import get_db
from backend.models import (
    Course, Division, CourseTeacherAllocation, LectureSchedule,
    AcademicSession, Attendance, AttendanceAuditTrail
)
from backend.schemas import (
    CourseAssignment, AttendanceSubmitRequest, AttendanceModifyRequest
)
from backend.dependencies import role_checker, AuthenticatedUser

router = APIRouter(tags=["Course Teacher"])

@router.get("/teacher/my-courses", response_model=List[CourseAssignment])
@router.get("/api/v1/teacher/my-courses", response_model=List[CourseAssignment])
def get_my_courses(
    current_user: AuthenticatedUser = Depends(role_checker(["COURSE_TEACHER", "CLASS_TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Returns only the active courses and divisions assigned to the logged-in teacher.
    """
    query = (
        db.query(
            Course.course_id,
            Course.course_code,
            Course.course_name,
            Course.semester,
            Course.credits,
            Division.div_id,
            Division.div_name,
            Division.room_no
        )
        .join(CourseTeacherAllocation, Course.course_id == CourseTeacherAllocation.course_id)
        .join(Division, CourseTeacherAllocation.div_id == Division.div_id)
        .filter(
            CourseTeacherAllocation.teacher_id == current_user.user_id,
            CourseTeacherAllocation.is_active == True
        )
        .all()
    )

    return [
        CourseAssignment(
            course_id=q.course_id,
            course_code=q.course_code,
            course_name=q.course_name,
            semester=q.semester,
            credits=q.credits,
            div_id=q.div_id,
            div_name=q.div_name,
            room_no=q.room_no
        )
        for q in query
    ]

@router.post("/attendance/submit")
@router.post("/api/v1/attendance/submit")
def submit_attendance(
    payload: AttendanceSubmitRequest,
    current_user: AuthenticatedUser = Depends(role_checker(["COURSE_TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Submits attendance for up to 60 students atomically within an explicit DB Transaction.
    If any single record fails or the network drops midway, a full ROLLBACK occurs.
    """
    # 1. Verify that this teacher is authorized to teach this course and division
    if not current_user.is_hod():
        is_assigned = db.query(CourseTeacherAllocation).filter(
            CourseTeacherAllocation.course_id == payload.course_id,
            CourseTeacherAllocation.div_id == payload.div_id,
            CourseTeacherAllocation.teacher_id == current_user.user_id,
            CourseTeacherAllocation.is_active == True
        ).first()

        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Security Violation: You are not assigned to Course {payload.course_id} for Division {payload.div_id}."
            )

    # 2. Derive Lecture_ID if omitted
    lecture_id = payload.lecture_id
    if not lecture_id:
        day_name = payload.session_date.strftime("%A")
        sched = db.query(LectureSchedule).filter(
            LectureSchedule.div_id == payload.div_id,
            LectureSchedule.course_id == payload.course_id,
            LectureSchedule.day_of_week == day_name,
            LectureSchedule.slot_no == payload.slot_no
        ).first()
        lecture_id = sched.lecture_id if sched else f"L_ADHOC_{payload.div_id}_{payload.slot_no}"

    # 3. Explicit Database Transaction with Full Rollback & Row-Level Locking Protection
    try:
        # Check or create Academic Session with Row-Level Locking (SELECT ... FOR UPDATE)
        session_query = db.query(AcademicSession).filter(
            AcademicSession.div_id == payload.div_id,
            AcademicSession.session_date == payload.session_date,
            AcademicSession.slot_no == payload.slot_no
        )
        if db.bind and db.bind.dialect.name == "postgresql":
            session_query = session_query.with_for_update()

        session_obj = session_query.first()

        if not session_obj:
            session_obj = AcademicSession(
                lecture_id=lecture_id,
                session_date=payload.session_date,
                slot_no=payload.slot_no,
                course_id=payload.course_id,
                div_id=payload.div_id,
                conducted_by_teacher_id=current_user.user_id,
                session_status="Conducted",
                topics_covered=payload.topics_covered or f"Lecture module covering {payload.course_id}."
            )
            db.add(session_obj)
            db.flush() # Flushes to get session_id while keeping transaction open

        session_id = session_obj.session_id

        # Insert or Upsert Attendance records with row locking
        submitted_count = 0
        for entry in payload.records:
            att_query = db.query(Attendance).filter(
                Attendance.student_id == entry.student_id,
                Attendance.course_id == payload.course_id,
                Attendance.attendance_date == payload.session_date,
                Attendance.slot_no == payload.slot_no
            )
            if db.bind and db.bind.dialect.name == "postgresql":
                att_query = att_query.with_for_update()
            
            existing_att = att_query.first()

            if existing_att:
                existing_att.status = entry.status
                existing_att.marked_by_emp_id = current_user.user_id
                existing_att.last_modified_at = datetime.utcnow()
            else:
                new_att = Attendance(
                    session_id=session_id,
                    student_id=entry.student_id,
                    course_id=payload.course_id,
                    attendance_date=payload.session_date,
                    slot_no=payload.slot_no,
                    status=entry.status,
                    marked_by_emp_id=current_user.user_id
                )
                db.add(new_att)
            
            submitted_count += 1

        # Commit only if all student entries processed without exception
        db.commit()
        return {
            "status": "SUCCESS",
            "message": f"Successfully recorded attendance for {submitted_count} students in Division {payload.div_id}.",
            "session_id": session_id,
            "session_date": str(payload.session_date),
            "slot_no": payload.slot_no
        }

    except Exception as e:
        db.rollback() # Complete rollback to prevent partial corruption
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database transaction aborted and rolled back: {str(e)}"
        )

@router.put("/attendance/modify")
@router.put("/api/v1/attendance/modify")
def modify_attendance(
    payload: AttendanceModifyRequest,
    request: Request,
    current_user: AuthenticatedUser = Depends(role_checker(["COURSE_TEACHER", "CLASS_TEACHER"])),
    db: Session = Depends(get_db)
):
    """
    Modifies an attendance record and automatically creates an immutable Audit Trail entry.
    """
    att = db.query(Attendance).filter(Attendance.attendance_id == payload.attendance_id).first()
    if not att:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found.")

    old_status = att.status
    new_status = payload.new_status.strip()

    if old_status == new_status:
        return {"status": "UNCHANGED", "message": f"Attendance is already '{old_status}'."}

    client_ip = request.client.host if request.client else "127.0.0.1"

    try:
        # Update attendance
        att.status = new_status
        att.last_modified_at = datetime.utcnow()

        # Insert Audit Trail
        audit_entry = AttendanceAuditTrail(
            attendance_id=att.attendance_id,
            old_value=old_status,
            new_value=new_status,
            modified_by_emp_id=current_user.user_id,
            modification_timestamp=datetime.utcnow(),
            reason=payload.reason.strip(),
            ip_address=client_ip
        )
        db.add(audit_entry)
        db.commit()

        return {
            "status": "SUCCESS",
            "message": f"Attendance corrected from '{old_status}' to '{new_status}' successfully.",
            "audit_id": audit_entry.audit_id,
            "student_id": att.student_id,
            "attendance_id": att.attendance_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Modification failed: {str(e)}")
