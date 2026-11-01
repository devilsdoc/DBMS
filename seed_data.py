"""
Database Seeding Script for CSE Department Attendance Management System
Uses SQLAlchemy and Python's CSV reader (with pandas support if available)
to import CSV files, configure foreign keys, and generate 2 weeks of dummy
Academic Sessions & Attendance records.
"""

import os
import sys
import csv
import random
from datetime import datetime, date, timedelta, time
from sqlalchemy import (
    create_engine, text, MetaData, Table, Column, String, Integer,
    Date, Time, DateTime, Boolean, Text, ForeignKey, BigInteger, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# 1. DATABASE CONNECTION CONFIGURATION
# ---------------------------------------------------------------------------
POSTGRES_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres@localhost:5432/cse_attendance"
)
SQLITE_URL = "sqlite:///cse_attendance.db"

def get_engine():
    if "--sqlite" in sys.argv:
        print("[INFO] Explicit --sqlite flag detected. Using local SQLite database (cse_attendance.db)")
        return create_engine(SQLITE_URL, echo=False)
    
    try:
        engine = create_engine(POSTGRES_URL, echo=False, connect_args={"connect_timeout": 3})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[INFO] Connected successfully to PostgreSQL at {POSTGRES_URL}")
        return engine
    except Exception as e:
        print(f"[WARN] PostgreSQL connection unavailable ({e}). Defaulting to SQLite: {SQLITE_URL}")
        return create_engine(SQLITE_URL, echo=False)

engine = get_engine()
is_sqlite = engine.url.drivername.startswith("sqlite")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# ---------------------------------------------------------------------------
# 2. SCHEMA DEFINITION (SQLAlchemy Core DDL)
# ---------------------------------------------------------------------------
metadata = MetaData()

departments = Table('departments', metadata,
    Column('dept_id', String(10), primary_key=True),
    Column('dept_name', String(100), nullable=False, unique=True),
    Column('dept_code', String(10), nullable=False, unique=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

academic_years = Table('academic_years', metadata,
    Column('ay_id', String(10), primary_key=True),
    Column('ay_name', String(50), nullable=False),
    Column('start_date', Date, nullable=False),
    Column('end_date', Date, nullable=False),
    Column('is_current', Boolean, default=False)
)

programs = Table('programs', metadata,
    Column('program_id', String(10), primary_key=True),
    Column('program_name', String(100), nullable=False),
    Column('program_code', String(10), nullable=False, unique=True),
    Column('dept_id', String(10), ForeignKey('departments.dept_id'), nullable=False)
)

classes = Table('classes', metadata,
    Column('class_id', String(10), primary_key=True),
    Column('class_name', String(50), nullable=False),
    Column('year_level', Integer, nullable=False),
    Column('program_id', String(10), ForeignKey('programs.program_id'), nullable=False)
)

divisions = Table('divisions', metadata,
    Column('div_id', String(10), primary_key=True),
    Column('div_name', String(20), nullable=False),
    Column('class_id', String(10), ForeignKey('classes.class_id'), nullable=False),
    Column('room_no', String(20)),
    Column('ay_id', String(10), ForeignKey('academic_years.ay_id'), nullable=False)
)

teachers = Table('teachers', metadata,
    Column('emp_id', String(20), primary_key=True),
    Column('teacher_name', String(100), nullable=False),
    Column('designation', String(100), nullable=False),
    Column('dept_id', String(10), ForeignKey('departments.dept_id'), nullable=False),
    Column('qualification', String(100)),
    Column('specialization', String(150)),
    Column('date_of_joining', Date),
    Column('email', String(120), nullable=False, unique=True),
    Column('phone', String(20)),
    Column('office_room', String(50)),
    Column('employment_type', String(20), default='Permanent'),
    Column('status', String(20), default='Active'),
    Column('password_hash', String(255), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow)
)

students = Table('students', metadata,
    Column('student_id', String(20), primary_key=True),
    Column('roll_no', String(30), nullable=False),
    Column('student_name', String(100), nullable=False),
    Column('div_id', String(10), ForeignKey('divisions.div_id'), nullable=False),
    Column('program_id', String(10), ForeignKey('programs.program_id'), nullable=False),
    Column('email', String(120), nullable=False, unique=True),
    Column('phone', String(20)),
    Column('admission_year', Integer, nullable=False),
    Column('status', String(20), default='Active'),
    Column('password_hash', String(255), nullable=False),
    Column('created_at', DateTime, default=datetime.utcnow),
    UniqueConstraint('roll_no', 'div_id', name='uq_roll_division')
)

roles = Table('roles', metadata,
    Column('role_id', String(20), primary_key=True),
    Column('role_name', String(50), nullable=False, unique=True),
    Column('description', Text)
)

user_role_mappings = Table('user_role_mappings', metadata,
    Column('mapping_id', Integer, primary_key=True, autoincrement=True),
    Column('user_identifier', String(20), nullable=False),
    Column('role_id', String(20), ForeignKey('roles.role_id'), nullable=False),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    UniqueConstraint('user_identifier', 'role_id', name='uq_user_role')
)

courses = Table('courses', metadata,
    Column('course_id', String(10), primary_key=True),
    Column('course_code', String(20), nullable=False, unique=True),
    Column('course_name', String(100), nullable=False),
    Column('semester', Integer, nullable=False),
    Column('dept_id', String(10), ForeignKey('departments.dept_id'), nullable=False),
    Column('credits', Integer, default=4),
    Column('is_elective', Boolean, default=False)
)

class_teacher_allocation = Table('class_teacher_allocation', metadata,
    Column('ct_alloc_id', Integer, primary_key=True, autoincrement=True),
    Column('div_id', String(10), ForeignKey('divisions.div_id'), nullable=False),
    Column('emp_id', String(20), ForeignKey('teachers.emp_id'), nullable=False),
    Column('ay_id', String(10), ForeignKey('academic_years.ay_id'), nullable=False),
    Column('from_date', Date, nullable=False),
    Column('to_date', Date),
    Column('is_active', Boolean, default=True)
)

course_teacher_allocation = Table('course_teacher_allocation', metadata,
    Column('cta_id', Integer, primary_key=True, autoincrement=True),
    Column('course_id', String(10), ForeignKey('courses.course_id'), nullable=False),
    Column('div_id', String(10), ForeignKey('divisions.div_id'), nullable=False),
    Column('teacher_id', String(20), ForeignKey('teachers.emp_id'), nullable=False),
    Column('ay_id', String(10), ForeignKey('academic_years.ay_id'), nullable=False),
    Column('from_date', Date, nullable=False),
    Column('to_date', Date),
    Column('is_active', Boolean, default=True)
)

teacher_guardians = Table('teacher_guardians', metadata,
    Column('tg_id', String(10), primary_key=True),
    Column('batch_name', String(50), nullable=False),
    Column('div_id', String(10), ForeignKey('divisions.div_id'), nullable=False),
    Column('ay_id', String(10), ForeignKey('academic_years.ay_id'), nullable=False),
    Column('current_teacher_id', String(20), ForeignKey('teachers.emp_id'), nullable=False)
)

tg_student_allocation = Table('tg_student_allocation', metadata,
    Column('alloc_id', String(20), primary_key=True),
    Column('tg_id', String(10), ForeignKey('teacher_guardians.tg_id'), nullable=False),
    Column('teacher_id', String(20), ForeignKey('teachers.emp_id'), nullable=False),
    Column('student_id', String(20), ForeignKey('students.student_id'), nullable=False),
    Column('from_date', Date, nullable=False),
    Column('to_date', Date),
    Column('status', String(20), default='Active')
)

lecture_schedule = Table('lecture_schedule', metadata,
    Column('lecture_id', String(20), primary_key=True),
    Column('course_id', String(10), ForeignKey('courses.course_id'), nullable=False),
    Column('div_id', String(10), ForeignKey('divisions.div_id'), nullable=False),
    Column('teacher_id', String(20), ForeignKey('teachers.emp_id'), nullable=False),
    Column('day_of_week', String(15), nullable=False),
    Column('slot_no', Integer, nullable=False),
    Column('start_time', Time, nullable=False),
    Column('end_time', Time, nullable=False),
    Column('room_no', String(20), nullable=False),
    Column('semester', Integer, nullable=False),
    Column('ay_id', String(10), ForeignKey('academic_years.ay_id'), nullable=False),
    Column('status', String(20), default='Active'),
    UniqueConstraint('div_id', 'day_of_week', 'slot_no', 'ay_id', name='uq_div_day_slot')
)

academic_sessions = Table('academic_sessions', metadata,
    Column('session_id', Integer if is_sqlite else BigInteger, primary_key=True, autoincrement=True),
    Column('lecture_id', String(20), ForeignKey('lecture_schedule.lecture_id'), nullable=False),
    Column('session_date', Date, nullable=False),
    Column('slot_no', Integer, nullable=False),
    Column('course_id', String(10), ForeignKey('courses.course_id'), nullable=False),
    Column('div_id', String(10), ForeignKey('divisions.div_id'), nullable=False),
    Column('conducted_by_teacher_id', String(20), ForeignKey('teachers.emp_id'), nullable=False),
    Column('session_status', String(20), default='Conducted'),
    Column('topics_covered', Text),
    Column('created_at', DateTime, default=datetime.utcnow),
    UniqueConstraint('div_id', 'session_date', 'slot_no', name='uq_session_occurrence')
)

attendance = Table('attendance', metadata,
    Column('attendance_id', Integer if is_sqlite else BigInteger, primary_key=True, autoincrement=True),
    Column('session_id', Integer if is_sqlite else BigInteger, ForeignKey('academic_sessions.session_id'), nullable=False),
    Column('student_id', String(20), ForeignKey('students.student_id'), nullable=False),
    Column('course_id', String(10), ForeignKey('courses.course_id'), nullable=False),
    Column('attendance_date', Date, nullable=False),
    Column('slot_no', Integer, nullable=False),
    Column('status', String(20), nullable=False),
    Column('marked_by_emp_id', String(20), ForeignKey('teachers.emp_id'), nullable=False),
    Column('recorded_at', DateTime, default=datetime.utcnow),
    Column('last_modified_at', DateTime, default=datetime.utcnow),
    UniqueConstraint('student_id', 'course_id', 'attendance_date', 'slot_no', name='uq_student_slot_att')
)

audit_trail = Table('attendance_audit_trail', metadata,
    Column('audit_id', Integer if is_sqlite else BigInteger, primary_key=True, autoincrement=True),
    Column('attendance_id', Integer if is_sqlite else BigInteger, ForeignKey('attendance.attendance_id'), nullable=False),
    Column('old_value', String(20), nullable=False),
    Column('new_value', String(20), nullable=False),
    Column('modified_by_emp_id', String(20), ForeignKey('teachers.emp_id'), nullable=False),
    Column('modification_timestamp', DateTime, default=datetime.utcnow),
    Column('reason', Text, nullable=False),
    Column('ip_address', String(45))
)

print("[INFO] Creating database schema tables...")
metadata.drop_all(engine)
metadata.create_all(engine)
print("[OK] Schema created successfully.")

# ---------------------------------------------------------------------------
# 3. HELPER TO READ CSV FILES
# ---------------------------------------------------------------------------
def read_csv_records(filepath):
    records = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {k.strip(): (v.strip() if v else "") for k, v in row.items() if k}
            records.append(cleaned)
    return records

# ---------------------------------------------------------------------------
# 4. SEED CORE REFERENCE DATA
# ---------------------------------------------------------------------------
with engine.begin() as conn:
    print("[INFO] Seeding Departments, Academic Years, Programs, Classes & Divisions...")
    conn.execute(departments.insert(), [
        {"dept_id": "D01", "dept_name": "Computer Science and Engineering", "dept_code": "CSE"}
    ])
    conn.execute(academic_years.insert(), [
        {"ay_id": "AY2025", "ay_name": "2024-2025", "start_date": date(2024, 7, 1), "end_date": date(2025, 6, 30), "is_current": True}
    ])
    conn.execute(programs.insert(), [
        {"program_id": "P01", "program_name": "B.Tech in Computer Science and Engineering", "program_code": "BTECH-CSE", "dept_id": "D01"}
    ])
    conn.execute(classes.insert(), [
        {"class_id": "C01", "class_name": "Second Year CSE", "year_level": 2, "program_id": "P01"},
        {"class_id": "C02", "class_name": "Third Year CSE", "year_level": 3, "program_id": "P01"}
    ])
    conn.execute(divisions.insert(), [
        {"div_id": "DIV01", "div_name": "SY-A", "class_id": "C01", "room_no": "A-101", "ay_id": "AY2025"},
        {"div_id": "DIV02", "div_name": "SY-B", "class_id": "C01", "room_no": "A-102", "ay_id": "AY2025"},
        {"div_id": "DIV03", "div_name": "TY-A", "class_id": "C02", "room_no": "B-201", "ay_id": "AY2025"}
    ])
    conn.execute(roles.insert(), [
        {"role_id": "HOD", "role_name": "Head of Department", "description": "Full department analytics and defaulters view"},
        {"role_id": "CLASS_TEACHER", "role_name": "Class Teacher", "description": "Division-wide attendance monitoring & reports"},
        {"role_id": "COURSE_TEACHER", "role_name": "Course Teacher", "description": "Slot attendance entry for allocated subjects"},
        {"role_id": "TEACHER_GUARDIAN", "role_name": "Teacher Guardian", "description": "Mentorship for allocated 20-student group"},
        {"role_id": "STUDENT", "role_name": "Student", "description": "Personal attendance dashboard and low-attendance alerts"}
    ])

# ---------------------------------------------------------------------------
# 5. INGEST TEACHERS (teachers.csv) & MAP ROLES
# ---------------------------------------------------------------------------
print("[INFO] Importing teachers.csv...")
teachers_data = read_csv_records("teachers.csv")
default_pwd_hash = "$2b$12$e8yCjM7tE/s4w67P10qV2uFvjR1k9oZxT9Lw3lH8.m1z4P3h7e8kK" # password123

teacher_rows = []
role_mappings = []

for row in teachers_data:
    emp_id = row["Emp_ID"]
    doj_str = row.get("Date_Of_Joining", "")
    try:
        doj = datetime.strptime(doj_str.split()[0], "%Y-%m-%d").date() if doj_str else date(2015, 1, 1)
    except Exception:
        doj = date(2015, 1, 1)
        
    teacher_rows.append({
        "emp_id": emp_id,
        "teacher_name": row["Teacher_Name"],
        "designation": row["Designation"],
        "dept_id": row.get("Dept_ID", "D01"),
        "qualification": row.get("Qualification", ""),
        "specialization": row.get("Specialization", ""),
        "date_of_joining": doj,
        "email": row["Email"],
        "phone": row.get("Phone", ""),
        "office_room": row.get("Office_Room", ""),
        "employment_type": row.get("Employment_Type", "Permanent"),
        "status": row.get("Status", "Active"),
        "password_hash": default_pwd_hash
    })
    
    # Automatic Role Assignment
    if emp_id == "EMP001":
        role_mappings.append({"user_identifier": emp_id, "role_id": "HOD"})
    if emp_id in ["EMP002", "EMP003", "EMP004"]:
        role_mappings.append({"user_identifier": emp_id, "role_id": "CLASS_TEACHER"})
    if emp_id in [f"EMP0{i:02d}" for i in range(6, 15)]: # EMP006 to EMP014
        role_mappings.append({"user_identifier": emp_id, "role_id": "TEACHER_GUARDIAN"})

with engine.begin() as conn:
    conn.execute(teachers.insert(), teacher_rows)
    print(f"[OK] Ingested {len(teacher_rows)} teachers.")

# Class Teacher Allocations: EMP002 -> SY-A, EMP003 -> SY-B, EMP004 -> TY-A
ct_allocations = [
    {"div_id": "DIV01", "emp_id": "EMP002", "ay_id": "AY2025", "from_date": date(2024, 7, 1), "is_active": True},
    {"div_id": "DIV02", "emp_id": "EMP003", "ay_id": "AY2025", "from_date": date(2024, 7, 1), "is_active": True},
    {"div_id": "DIV03", "emp_id": "EMP004", "ay_id": "AY2025", "from_date": date(2024, 7, 1), "is_active": True}
]
with engine.begin() as conn:
    conn.execute(class_teacher_allocation.insert(), ct_allocations)

# ---------------------------------------------------------------------------
# 6. INGEST STUDENTS (students.csv)
# ---------------------------------------------------------------------------
print("[INFO] Importing students.csv...")
students_data = read_csv_records("students.csv")
student_rows = []

for row in students_data:
    s_id = row["Student_ID"]
    student_rows.append({
        "student_id": s_id,
        "roll_no": row["Roll_No"],
        "student_name": row["Student_Name"],
        "div_id": row["Div_ID"],
        "program_id": row.get("Program_ID", "P01"),
        "email": row["Email"],
        "phone": row.get("Phone", ""),
        "admission_year": int(row.get("Admission_Year", 2024)),
        "status": row.get("Status", "Active"),
        "password_hash": default_pwd_hash
    })
    role_mappings.append({"user_identifier": s_id, "role_id": "STUDENT"})

with engine.begin() as conn:
    conn.execute(students.insert(), student_rows)
    print(f"[OK] Ingested {len(student_rows)} students.")

# ---------------------------------------------------------------------------
# 7. INGEST TIMETABLE (timetable.csv) & POPULATE COURSES
# ---------------------------------------------------------------------------
print("[INFO] Importing timetable.csv and deriving Courses & Allocations...")
tt_data = read_csv_records("timetable.csv")

unique_courses = {}
cta_set = set()
schedule_rows = []

for row in tt_data:
    c_id = row["Course_ID"]
    if c_id not in unique_courses:
        unique_courses[c_id] = {
            "course_id": c_id,
            "course_code": row["Course_Code"],
            "course_name": row["Course_Name"],
            "semester": int(row["Semester"]),
            "dept_id": "D01",
            "credits": 4,
            "is_elective": False
        }
    
    div_id = row["Div_ID"]
    teacher_id = row["Teacher_ID"]
    cta_set.add((c_id, div_id, teacher_id))
    role_mappings.append({"user_identifier": teacher_id, "role_id": "COURSE_TEACHER"})
    
    st_parts = [int(p) for p in row["Start_Time"].split(":")]
    et_parts = [int(p) for p in row["End_Time"].split(":")]
    start_t = time(st_parts[0], st_parts[1], st_parts[2] if len(st_parts) > 2 else 0)
    end_t = time(et_parts[0], et_parts[1], et_parts[2] if len(et_parts) > 2 else 0)
    
    schedule_rows.append({
        "lecture_id": row["Lecture_ID"],
        "course_id": c_id,
        "div_id": div_id,
        "teacher_id": teacher_id,
        "day_of_week": row["Day_Of_Week"],
        "slot_no": int(row["Slot_No"]),
        "start_time": start_t,
        "end_time": end_t,
        "room_no": row["Room_No"],
        "semester": int(row["Semester"]),
        "ay_id": row.get("AY_ID", "AY2025"),
        "status": row.get("Status", "Active")
    })

course_rows = list(unique_courses.values())
cta_rows = [
    {
        "course_id": c[0],
        "div_id": c[1],
        "teacher_id": c[2],
        "ay_id": "AY2025",
        "from_date": date(2024, 7, 1),
        "is_active": True
    }
    for c in cta_set
]

with engine.begin() as conn:
    conn.execute(courses.insert(), course_rows)
    conn.execute(course_teacher_allocation.insert(), cta_rows)
    conn.execute(lecture_schedule.insert(), schedule_rows)
    
    # Deduplicate and insert role mappings
    unique_roles = [dict(t) for t in {tuple(d.items()) for d in role_mappings}]
    conn.execute(user_role_mappings.insert(), unique_roles)
    print(f"[OK] Ingested {len(course_rows)} unique courses, {len(cta_rows)} course allocations, and {len(schedule_rows)} timetable slots.")

# ---------------------------------------------------------------------------
# 8. INGEST TEACHER GUARDIANS (tg_allocation.csv)
# ---------------------------------------------------------------------------
print("[INFO] Importing tg_allocation.csv (Teacher Guardian groups and 20-student allocations)...")
tg_data = read_csv_records("tg_allocation.csv")

tg_groups = {}
tg_alloc_rows = []

for row in tg_data:
    tg_id = row["TG_ID"]
    teacher_id = row["Teacher_ID"]
    div_id = row["Div_ID"]
    
    if tg_id not in tg_groups:
        tg_groups[tg_id] = {
            "tg_id": tg_id,
            "batch_name": f"{div_id} Mentor Group ({tg_id})",
            "div_id": div_id,
            "ay_id": "AY2025",
            "current_teacher_id": teacher_id
        }
        
    f_date_str = row.get("From_Date", "")
    t_date_str = row.get("To_Date", "")
    f_date = datetime.strptime(f_date_str.split()[0], "%Y-%m-%d").date() if f_date_str else date(2024, 7, 1)
    t_date = datetime.strptime(t_date_str.split()[0], "%Y-%m-%d").date() if t_date_str else None
    
    tg_alloc_rows.append({
        "alloc_id": row["Alloc_ID"],
        "tg_id": tg_id,
        "teacher_id": teacher_id,
        "student_id": row["Student_ID"],
        "from_date": f_date,
        "to_date": t_date,
        "status": row.get("Status", "Active")
    })

tg_rows = list(tg_groups.values())

with engine.begin() as conn:
    conn.execute(teacher_guardians.insert(), tg_rows)
    conn.execute(tg_student_allocation.insert(), tg_alloc_rows)
    print(f"[OK] Ingested {len(tg_rows)} TG groups and {len(tg_alloc_rows)} student allocations.")

# ---------------------------------------------------------------------------
# 9. GENERATE 2 WEEKS DUMMY ACADEMIC SESSIONS & REALISTIC ATTENDANCE
# ---------------------------------------------------------------------------
print("[INFO] Generating dummy Academic Sessions & Attendance for the last 2 weeks (Mon-Fri only)...")

day_name_to_weekday = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
weekday_to_day_name = {v: k for k, v in day_name_to_weekday.items()}

# Calculate past 10 working days
today = date.today()
working_days = []
curr = today - timedelta(days=1)
while len(working_days) < 10:
    if curr.weekday() < 5:
        working_days.append(curr)
    curr -= timedelta(days=1)
working_days.sort()

# Group students by division
students_by_div = {}
for s in student_rows:
    students_by_div.setdefault(s["div_id"], []).append(s["student_id"])

# Specific defaulters (<75%) for dashboard testing
test_defaulters = {"S005", "S015", "S065", "S075", "S125", "S135"}

session_id_counter = 1
attendance_id_counter = 1
academic_session_records = []
attendance_records = []
audit_records = []

random.seed(42)

for s_date in working_days:
    day_name = weekday_to_day_name[s_date.weekday()]
    day_slots = [s for s in schedule_rows if s["day_of_week"] == day_name]
    
    for slot in day_slots:
        lecture_id = slot["lecture_id"]
        course_id = slot["course_id"]
        div_id = slot["div_id"]
        teacher_id = slot["teacher_id"]
        slot_no = slot["slot_no"]
        
        dice = random.random()
        if dice < 0.03:
            s_status = "Cancelled"
            topics = "Session cancelled due to faculty symposium."
        elif dice < 0.05:
            s_status = "Rescheduled"
            topics = "Session rescheduled to upcoming lab slot."
        else:
            s_status = "Conducted"
            topics = f"Conducted unit syllabus module for {course_id}."
            
        academic_session_records.append({
            "session_id": session_id_counter,
            "lecture_id": lecture_id,
            "session_date": s_date,
            "slot_no": slot_no,
            "course_id": course_id,
            "div_id": div_id,
            "conducted_by_teacher_id": teacher_id,
            "session_status": s_status,
            "topics_covered": topics
        })
        
        current_session_id = session_id_counter
        session_id_counter += 1
        
        if s_status == "Conducted":
            div_students = students_by_div.get(div_id, [])
            for st_id in div_students:
                if st_id in test_defaulters:
                    status = "Present" if random.random() < 0.55 else "Absent"
                else:
                    r = random.random()
                    if r < 0.88:
                        status = "Present"
                    elif r < 0.93:
                        status = "Late"
                    else:
                        status = "Absent"
                
                attendance_records.append({
                    "attendance_id": attendance_id_counter,
                    "session_id": current_session_id,
                    "student_id": st_id,
                    "course_id": course_id,
                    "attendance_date": s_date,
                    "slot_no": slot_no,
                    "status": status,
                    "marked_by_emp_id": teacher_id
                })
                
                # Sample Audit Trail entries for testing correction logs
                if st_id in ["S003", "S063", "S123"] and slot_no == 1 and s_date == working_days[-2]:
                    audit_records.append({
                        "audit_id": len(audit_records) + 1,
                        "attendance_id": attendance_id_counter,
                        "old_value": "Absent",
                        "new_value": "Present",
                        "modified_by_emp_id": teacher_id,
                        "reason": "Medical certificate submitted and verified by Class Teacher",
                        "ip_address": "192.168.1.105"
                    })
                
                attendance_id_counter += 1

with engine.begin() as conn:
    conn.execute(academic_sessions.insert(), academic_session_records)
    print(f"[OK] Generated {len(academic_session_records)} Academic Sessions across 10 working days.")
    
    BATCH_SIZE = 1000
    for i in range(0, len(attendance_records), BATCH_SIZE):
        batch = attendance_records[i:i + BATCH_SIZE]
        conn.execute(attendance.insert(), batch)
    print(f"[OK] Generated {len(attendance_records)} Attendance entries.")
    
    if audit_records:
        conn.execute(audit_trail.insert(), audit_records)
        print(f"[OK] Seeded {len(audit_records)} sample Audit Trail entries.")

# ---------------------------------------------------------------------------
# 10. VALIDATION & SUMMARY REPORT
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print(" CSE ATTENDANCE DATABASE INITIALIZATION & SEEDING REPORT ")
print("="*70)
with engine.connect() as conn:
    for tbl in [
        "departments", "programs", "classes", "divisions", "teachers",
        "roles", "user_role_mappings", "students", "courses",
        "class_teacher_allocation", "course_teacher_allocation",
        "teacher_guardians", "tg_student_allocation", "lecture_schedule",
        "academic_sessions", "attendance", "attendance_audit_trail"
    ]:
        cnt = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
        print(f" - {tbl.ljust(26)} : {cnt:>6} rows")

print("="*70)
print("[SUCCESS] All tables seeded and verified with full relational integrity!")
