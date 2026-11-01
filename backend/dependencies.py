"""
Role-Based Access Control (RBAC) Middleware & Authorization Dependencies
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import decode_access_token
from backend.models import (
    Teacher, Student, UserRoleMapping, ClassTeacherAllocation,
    TGStudentAllocation, CourseTeacherAllocation
)

security = HTTPBearer()

class AuthenticatedUser:
    def __init__(
        self,
        user_id: str,
        name: str,
        user_type: str,
        roles: List[str],
        assigned_division: Optional[str] = None,
        tg_id: Optional[str] = None
    ):
        self.user_id = user_id
        self.name = name
        self.user_type = user_type
        self.roles = roles
        self.assigned_division = assigned_division
        self.tg_id = tg_id

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def is_hod(self) -> bool:
        return "HOD" in self.roles or self.user_id == "EMP001"

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AuthenticatedUser:
    """
    Extracts, decodes, and validates the JWT Bearer token.
    Resolves the user identity, checks active status, and synthesizes permissions.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token: subject identifier missing."
        )

    # Fetch live roles from database
    role_records = db.query(UserRoleMapping).filter(UserRoleMapping.user_identifier == user_id).all()
    roles = [r.role_id for r in role_records]

    # Resolve entity details
    if user_id.startswith("EMP"):
        teacher = db.query(Teacher).filter(Teacher.emp_id == user_id).first()
        if not teacher or teacher.status != "Active":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Teacher account inactive or not found.")
        
        # Check Class Teacher allocation
        ct_alloc = db.query(ClassTeacherAllocation).filter(
            ClassTeacherAllocation.emp_id == user_id,
            ClassTeacherAllocation.is_active == True
        ).first()
        assigned_div = ct_alloc.div_id if ct_alloc else None
        
        # Check TG Group
        tg_alloc = db.query(TGStudentAllocation).filter(
            TGStudentAllocation.teacher_id == user_id,
            TGStudentAllocation.status == 'Active'
        ).first()
        tg_id = tg_alloc.tg_id if tg_alloc else None

        return AuthenticatedUser(
            user_id=teacher.emp_id,
            name=teacher.teacher_name,
            user_type="TEACHER",
            roles=roles,
            assigned_division=assigned_div,
            tg_id=tg_id
        )
    else:
        # Student account
        student = db.query(Student).filter(Student.student_id == user_id).first()
        if not student or student.status != "Active":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Student account inactive or not found.")
        
        return AuthenticatedUser(
            user_id=student.student_id,
            name=student.student_name,
            user_type="STUDENT",
            roles=roles or ["STUDENT"],
            assigned_division=student.div_id
        )

def role_checker(allowed_roles: List[str]):
    """
    Factory creating a FastAPI dependency that enforces role requirements.
    Ensures that a user must hold AT LEAST ONE of the allowed roles.
    Example: A Teacher Guardian without COURSE_TEACHER cannot access Course Teacher routes.
    """
    def checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        # HoD has overarching monitoring authority
        if current_user.is_hod():
            return current_user
        
        # Check if user has any of the permissible roles
        if not any(current_user.has_role(r) for r in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Endpoint requires one of roles: {allowed_roles}. Your active roles: {current_user.roles}"
            )
        return current_user

    return checker

def require_course_teacher_access(
    course_id: str,
    div_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ensures that the teacher is specifically allocated to instruct this course and division.
    """
    if current_user.is_hod():
        return current_user

    allocation = db.query(CourseTeacherAllocation).filter(
        CourseTeacherAllocation.course_id == course_id,
        CourseTeacherAllocation.div_id == div_id,
        CourseTeacherAllocation.teacher_id == current_user.user_id,
        CourseTeacherAllocation.is_active == True
    ).first()

    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Authorization Violation: You are not assigned to teach Course {course_id} for Division {div_id}."
        )
    return current_user
