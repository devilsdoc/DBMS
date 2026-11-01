"""
Authentication Endpoints: Login, JWT Token Issuance, and User Profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Teacher, Student, UserRoleMapping, ClassTeacherAllocation, TGStudentAllocation
from backend.schemas import LoginRequest, TokenResponse, UserProfile
from backend.auth import verify_password, create_access_token
from backend.dependencies import get_current_user, AuthenticatedUser

router = APIRouter(tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
@router.post("/api/v1/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates Teacher (Emp_ID) or Student (Student_ID) using Bcrypt.
    Returns JWT containing all active roles, claims, and entity details.
    """
    username = request.username.strip()
    password = request.password.strip()

    user_obj = None
    user_type = None
    name = ""
    email = ""

    # 1. Search in Teachers
    if username.upper().startswith("EMP") or not username.upper().startswith("S"):
        teacher = db.query(Teacher).filter(Teacher.emp_id == username).first()
        if teacher:
            user_obj = teacher
            user_type = "TEACHER"
            name = teacher.teacher_name
            email = teacher.email

    # 2. Search in Students
    if not user_obj:
        student = db.query(Student).filter(Student.student_id == username).first()
        if student:
            user_obj = student
            user_type = "STUDENT"
            name = student.student_name
            email = student.email

    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials: User ID not found."
        )

    # 3. Bcrypt Password Verification
    if not verify_password(password, user_obj.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials: Incorrect password."
        )

    if user_obj.status != "Active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is currently {user_obj.status}. Please contact administration."
        )

    # 4. Fetch User Roles
    role_records = db.query(UserRoleMapping).filter(UserRoleMapping.user_identifier == username).all()
    roles = [r.role_id for r in role_records]
    if not roles:
        roles = ["STUDENT"] if user_type == "STUDENT" else ["COURSE_TEACHER"]

    # 5. Resolve Auxiliary Allocations
    assigned_division = None
    tg_id = None

    if user_type == "TEACHER":
        ct_alloc = db.query(ClassTeacherAllocation).filter(
            ClassTeacherAllocation.emp_id == username,
            ClassTeacherAllocation.is_active == True
        ).first()
        if ct_alloc:
            assigned_division = ct_alloc.div_id

        tg_alloc = db.query(TGStudentAllocation).filter(
            TGStudentAllocation.teacher_id == username,
            TGStudentAllocation.status == 'Active'
        ).first()
        if tg_alloc:
            tg_id = tg_alloc.tg_id
    else:
        assigned_division = getattr(user_obj, "div_id", None)

    # 6. Generate JWT Token
    jwt_claims = {
        "sub": username,
        "name": name,
        "email": email,
        "user_type": user_type,
        "roles": roles,
        "assigned_division": assigned_division,
        "tg_id": tg_id
    }
    token = create_access_token(jwt_claims)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserProfile(
            id=username,
            name=name,
            email=email,
            user_type=user_type,
            roles=roles,
            assigned_division=assigned_division,
            tg_id=tg_id
        )
    )

@router.get("/me", response_model=UserProfile)
@router.get("/api/v1/me", response_model=UserProfile)
def get_my_profile(current_user: AuthenticatedUser = Depends(get_current_user)):
    """Returns the authenticated profile of the caller."""
    return UserProfile(
        id=current_user.user_id,
        name=current_user.name,
        email=f"{current_user.user_id.lower()}@inst.edu",
        user_type=current_user.user_type,
        roles=current_user.roles,
        assigned_division=current_user.assigned_division,
        tg_id=current_user.tg_id
    )
