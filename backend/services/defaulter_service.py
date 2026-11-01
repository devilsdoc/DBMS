"""
Automated Defaulter Detection & Alert Generation Service
Runs daily at 6:00 PM (or on-demand) to identify students below 75% attendance
and generates alert records targeted to their assigned Teacher Guardian.
"""

from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models import (
    Student, Attendance, TGStudentAllocation, DefaulterAlert
)

def evaluate_and_generate_defaulter_alerts(db: Session) -> dict:
    """
    Scans all enrolled students. If a student's cumulative attendance drops below 75%,
    creates an alert record linked to the student's Teacher Guardian (TG).
    """
    today = date.today()
    students = db.query(Student).filter(Student.status == 'Active').all()

    new_alerts_created = 0
    defaulters_detected = 0

    for s in students:
        # Calculate overall attendance
        total_sessions = (
            db.query(func.count(Attendance.attendance_id))
            .filter(Attendance.student_id == s.student_id)
            .scalar() or 0
        )

        if total_sessions == 0:
            continue

        attended_sessions = (
            db.query(func.count(Attendance.attendance_id))
            .filter(
                Attendance.student_id == s.student_id,
                Attendance.status.in_(["Present", "Late"])
            )
            .scalar() or 0
        )

        pct = round((attended_sessions / total_sessions * 100), 2)

        if pct < 75.0:
            defaulters_detected += 1

            # Find TG allocation
            tg_alloc = db.query(TGStudentAllocation).filter(
                TGStudentAllocation.student_id == s.student_id,
                TGStudentAllocation.status == 'Active'
            ).first()

            tg_id = tg_alloc.tg_id if tg_alloc else None

            # Check if an alert was already logged today for this student
            existing_today = db.query(DefaulterAlert).filter(
                DefaulterAlert.student_id == s.student_id,
                DefaulterAlert.alert_date == today
            ).first()

            if not existing_today:
                alert = DefaulterAlert(
                    student_id=s.student_id,
                    div_id=s.div_id,
                    tg_id=tg_id,
                    attendance_percentage=pct,
                    alert_date=today,
                    is_read=False,
                    message=f"CRITICAL SHORTFALL: {s.student_name} ({s.roll_no}) attendance has dropped to {pct}% (< 75% threshold). Requires parent intimation.",
                    created_at=datetime.utcnow()
                )
                db.add(alert)
                new_alerts_created += 1

    db.commit()

    return {
        "status": "COMPLETED",
        "date": str(today),
        "total_scanned": len(students),
        "defaulters_detected": defaulters_detected,
        "new_alerts_created": new_alerts_created
    }
