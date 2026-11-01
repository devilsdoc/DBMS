"""
Pydantic Schemas for Request & Response Data Models
"""

from typing import List, Optional
from datetime import date, time, datetime
from pydantic import BaseModel, EmailStr

# --- Auth Schemas ---
class LoginRequest(BaseModel):
    username: str # Emp_ID (e.g. EMP001, EMP006) or Student_ID (e.g. S001)
    password: str

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    user_type: str # 'TEACHER' or 'STUDENT'
    roles: List[str]
    assigned_division: Optional[str] = None # e.g. 'DIV01' for Class Teachers
    tg_id: Optional[str] = None # e.g. 'TG01' for Teacher Guardians

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

# --- Teacher Schemas ---
class CourseAssignment(BaseModel):
    course_id: str
    course_code: str
    course_name: str
    div_id: str
    div_name: str
    semester: int
    credits: int
    room_no: Optional[str] = None

class StudentAttendanceEntry(BaseModel):
    student_id: str
    status: str # 'Present', 'Absent', 'Late', 'Excused'

class AttendanceSubmitRequest(BaseModel):
    session_date: date
    slot_no: int # 1 to 6
    course_id: str
    div_id: str
    lecture_id: Optional[str] = None
    topics_covered: Optional[str] = None
    records: List[StudentAttendanceEntry]

class AttendanceModifyRequest(BaseModel):
    attendance_id: int
    new_status: str # 'Present', 'Absent', 'Late', 'Excused'
    reason: str

# --- TG Schemas ---
class TGStudentInfo(BaseModel):
    student_id: str
    roll_no: str
    student_name: str
    div_id: str
    div_name: Optional[str] = None
    email: str
    phone: Optional[str] = None

class SubjectAttendanceDetail(BaseModel):
    course_id: str
    course_code: str
    course_name: str
    conducted: int
    attended: int
    percentage: float

class TGStudentAttendanceReport(BaseModel):
    student_id: str
    roll_no: str
    student_name: str
    div_id: str
    total_conducted: int
    total_attended: int
    attendance_percentage: float
    is_defaulter: bool
    subject_wise: List[SubjectAttendanceDetail]

# --- Student Schemas ---
class StudentAttendanceDashboard(BaseModel):
    student_id: str
    student_name: str
    roll_no: str
    div_id: str
    div_name: str
    total_conducted: int
    total_attended: int
    overall_percentage: float
    is_defaulter: bool
    courses: List[SubjectAttendanceDetail]
    absent_dates: List[dict]

# --- Division Reports Schemas ---
class DivisionReportResponse(BaseModel):
    div_id: str
    div_name: str
    class_name: str
    class_teacher_name: Optional[str] = None
    total_students: int
    total_sessions_conducted: int
    division_average_percentage: float
    defaulters_count: int
    defaulters: List[dict]
    course_statistics: List[dict]
