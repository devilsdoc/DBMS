"""
SQLAlchemy ORM Models for CSE Department Attendance Management System (3NF)
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Date, Time, DateTime, Boolean, Text,
    ForeignKey, BigInteger, UniqueConstraint
)
from sqlalchemy.orm import relationship
from backend.database import Base

class Department(Base):
    __tablename__ = 'departments'
    dept_id = Column(String(10), primary_key=True)
    dept_name = Column(String(100), nullable=False, unique=True)
    dept_code = Column(String(10), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AcademicYear(Base):
    __tablename__ = 'academic_years'
    ay_id = Column(String(10), primary_key=True)
    ay_name = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)

class Program(Base):
    __tablename__ = 'programs'
    program_id = Column(String(10), primary_key=True)
    program_name = Column(String(100), nullable=False)
    program_code = Column(String(10), nullable=False, unique=True)
    dept_id = Column(String(10), ForeignKey('departments.dept_id'), nullable=False)

class ClassEntity(Base):
    __tablename__ = 'classes'
    class_id = Column(String(10), primary_key=True)
    class_name = Column(String(50), nullable=False)
    year_level = Column(Integer, nullable=False)
    program_id = Column(String(10), ForeignKey('programs.program_id'), nullable=False)

class Division(Base):
    __tablename__ = 'divisions'
    div_id = Column(String(10), primary_key=True)
    div_name = Column(String(20), nullable=False)
    class_id = Column(String(10), ForeignKey('classes.class_id'), nullable=False)
    room_no = Column(String(20))
    ay_id = Column(String(10), ForeignKey('academic_years.ay_id'), nullable=False)

class Teacher(Base):
    __tablename__ = 'teachers'
    emp_id = Column(String(20), primary_key=True)
    teacher_name = Column(String(100), nullable=False)
    designation = Column(String(100), nullable=False)
    dept_id = Column(String(10), ForeignKey('departments.dept_id'), nullable=False)
    qualification = Column(String(100))
    specialization = Column(String(150))
    date_of_joining = Column(Date)
    email = Column(String(120), nullable=False, unique=True)
    phone = Column(String(20))
    office_room = Column(String(50))
    employment_type = Column(String(20), default='Permanent')
    status = Column(String(20), default='Active')
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Student(Base):
    __tablename__ = 'students'
    student_id = Column(String(20), primary_key=True)
    roll_no = Column(String(30), nullable=False)
    student_name = Column(String(100), nullable=False)
    div_id = Column(String(10), ForeignKey('divisions.div_id'), nullable=False)
    program_id = Column(String(10), ForeignKey('programs.program_id'), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    phone = Column(String(20))
    admission_year = Column(Integer, nullable=False)
    status = Column(String(20), default='Active')
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(String(20), primary_key=True)
    role_name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

class UserRoleMapping(Base):
    __tablename__ = 'user_role_mappings'
    mapping_id = Column(Integer, primary_key=True, autoincrement=True)
    user_identifier = Column(String(20), nullable=False)
    role_id = Column(String(20), ForeignKey('roles.role_id'), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

class Course(Base):
    __tablename__ = 'courses'
    course_id = Column(String(10), primary_key=True)
    course_code = Column(String(20), nullable=False, unique=True)
    course_name = Column(String(100), nullable=False)
    semester = Column(Integer, nullable=False)
    dept_id = Column(String(10), ForeignKey('departments.dept_id'), nullable=False)
    credits = Column(Integer, default=4)
    is_elective = Column(Boolean, default=False)

class ClassTeacherAllocation(Base):
    __tablename__ = 'class_teacher_allocation'
    ct_alloc_id = Column(Integer, primary_key=True, autoincrement=True)
    div_id = Column(String(10), ForeignKey('divisions.div_id'), nullable=False)
    emp_id = Column(String(20), ForeignKey('teachers.emp_id'), nullable=False)
    ay_id = Column(String(10), ForeignKey('academic_years.ay_id'), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date)
    is_active = Column(Boolean, default=True)

class CourseTeacherAllocation(Base):
    __tablename__ = 'course_teacher_allocation'
    cta_id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String(10), ForeignKey('courses.course_id'), nullable=False)
    div_id = Column(String(10), ForeignKey('divisions.div_id'), nullable=False)
    teacher_id = Column(String(20), ForeignKey('teachers.emp_id'), nullable=False)
    ay_id = Column(String(10), ForeignKey('academic_years.ay_id'), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date)
    is_active = Column(Boolean, default=True)

class TeacherGuardian(Base):
    __tablename__ = 'teacher_guardians'
    tg_id = Column(String(10), primary_key=True)
    batch_name = Column(String(50), nullable=False)
    div_id = Column(String(10), ForeignKey('divisions.div_id'), nullable=False)
    ay_id = Column(String(10), ForeignKey('academic_years.ay_id'), nullable=False)
    current_teacher_id = Column(String(20), ForeignKey('teachers.emp_id'), nullable=False)

class TGStudentAllocation(Base):
    __tablename__ = 'tg_student_allocation'
    alloc_id = Column(String(20), primary_key=True)
    tg_id = Column(String(10), ForeignKey('teacher_guardians.tg_id'), nullable=False)
    teacher_id = Column(String(20), ForeignKey('teachers.emp_id'), nullable=False)
    student_id = Column(String(20), ForeignKey('students.student_id'), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date)
    status = Column(String(20), default='Active')

class LectureSchedule(Base):
    __tablename__ = 'lecture_schedule'
    lecture_id = Column(String(20), primary_key=True)
    course_id = Column(String(10), ForeignKey('courses.course_id'), nullable=False)
    div_id = Column(String(10), ForeignKey('divisions.div_id'), nullable=False)
    teacher_id = Column(String(20), ForeignKey('teachers.emp_id'), nullable=False)
    day_of_week = Column(String(15), nullable=False)
    slot_no = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    room_no = Column(String(20), nullable=False)
    semester = Column(Integer, nullable=False)
    ay_id = Column(String(10), ForeignKey('academic_years.ay_id'), nullable=False)
    status = Column(String(20), default='Active')

class AcademicSession(Base):
    __tablename__ = 'academic_sessions'
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    lecture_id = Column(String(20), ForeignKey('lecture_schedule.lecture_id'), nullable=False)
    session_date = Column(Date, nullable=False)
    slot_no = Column(Integer, nullable=False)
    course_id = Column(String(10), ForeignKey('courses.course_id'), nullable=False)
    div_id = Column(String(10), ForeignKey('divisions.div_id'), nullable=False)
    conducted_by_teacher_id = Column(String(20), ForeignKey('teachers.emp_id'), nullable=False)
    session_status = Column(String(20), default='Conducted')
    topics_covered = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Attendance(Base):
    __tablename__ = 'attendance'
    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('academic_sessions.session_id'), nullable=False)
    student_id = Column(String(20), ForeignKey('students.student_id'), nullable=False)
    course_id = Column(String(10), ForeignKey('courses.course_id'), nullable=False)
    attendance_date = Column(Date, nullable=False)
    slot_no = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False) # 'Present', 'Absent', 'Late', 'Excused'
    marked_by_emp_id = Column(String(20), ForeignKey('teachers.emp_id'), nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    last_modified_at = Column(DateTime, default=datetime.utcnow)

class AttendanceAuditTrail(Base):
    __tablename__ = 'attendance_audit_trail'
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    attendance_id = Column(Integer, ForeignKey('attendance.attendance_id'), nullable=False)
    old_value = Column(String(20), nullable=False)
    new_value = Column(String(20), nullable=False)
    modified_by_emp_id = Column(String(20), ForeignKey('teachers.emp_id'), nullable=False)
    modification_timestamp = Column(DateTime, default=datetime.utcnow)
    reason = Column(Text, nullable=False)
    ip_address = Column(String(45))

class DefaulterAlert(Base):
    __tablename__ = 'defaulter_alerts'
    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String(20), ForeignKey('students.student_id'), nullable=False)
    div_id = Column(String(10), ForeignKey('divisions.div_id'), nullable=False)
    tg_id = Column(String(10), ForeignKey('teacher_guardians.tg_id'), nullable=True)
    attendance_percentage = Column(Float, nullable=False)
    alert_date = Column(Date, nullable=False)
    is_read = Column(Boolean, default=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
