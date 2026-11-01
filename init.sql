-- ============================================================================
-- CSE DEPARTMENT ATTENDANCE MANAGEMENT SYSTEM - DATABASE INITIALIZATION
-- ============================================================================

-- Drop tables if re-initializing (in reverse FK order)
DROP TABLE IF EXISTS Attendance_Audit_Trail CASCADE;
DROP TABLE IF EXISTS Attendance CASCADE;
DROP TABLE IF EXISTS Academic_Sessions CASCADE;
DROP TABLE IF EXISTS Lecture_Schedule CASCADE;
DROP TABLE IF EXISTS TG_Student_Allocation CASCADE;
DROP TABLE IF EXISTS Teacher_Guardians CASCADE;
DROP TABLE IF EXISTS Course_Teacher_Allocation CASCADE;
DROP TABLE IF EXISTS Class_Teacher_Allocation CASCADE;
DROP TABLE IF EXISTS Courses CASCADE;
DROP TABLE IF EXISTS User_Role_Mappings CASCADE;
DROP TABLE IF EXISTS Roles CASCADE;
DROP TABLE IF EXISTS Students CASCADE;
DROP TABLE IF EXISTS Teachers CASCADE;
DROP TABLE IF EXISTS Divisions CASCADE;
DROP TABLE IF EXISTS Classes CASCADE;
DROP TABLE IF EXISTS Programs CASCADE;
DROP TABLE IF EXISTS Academic_Years CASCADE;
DROP TABLE IF EXISTS Departments CASCADE;

-- 1. Departments, Programs & Academic Years
CREATE TABLE Departments (
    Dept_ID VARCHAR(10) PRIMARY KEY,
    Dept_Name VARCHAR(100) NOT NULL UNIQUE,
    Dept_Code VARCHAR(10) NOT NULL UNIQUE,
    Created_At TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Academic_Years (
    AY_ID VARCHAR(10) PRIMARY KEY,
    AY_Name VARCHAR(50) NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    Is_Current BOOLEAN DEFAULT FALSE,
    CONSTRAINT chk_ay_dates CHECK (End_Date > Start_Date)
);

CREATE TABLE Programs (
    Program_ID VARCHAR(10) PRIMARY KEY,
    Program_Name VARCHAR(100) NOT NULL,
    Program_Code VARCHAR(10) NOT NULL UNIQUE,
    Dept_ID VARCHAR(10) NOT NULL REFERENCES Departments(Dept_ID) ON DELETE RESTRICT
);

CREATE TABLE Classes (
    Class_ID VARCHAR(10) PRIMARY KEY,
    Class_Name VARCHAR(50) NOT NULL,
    Year_Level INT NOT NULL CHECK (Year_Level BETWEEN 1 AND 4),
    Program_ID VARCHAR(10) NOT NULL REFERENCES Programs(Program_ID) ON DELETE RESTRICT
);

CREATE TABLE Divisions (
    Div_ID VARCHAR(10) PRIMARY KEY,
    Div_Name VARCHAR(20) NOT NULL,
    Class_ID VARCHAR(10) NOT NULL REFERENCES Classes(Class_ID) ON DELETE RESTRICT,
    Room_No VARCHAR(20),
    AY_ID VARCHAR(10) NOT NULL REFERENCES Academic_Years(AY_ID) ON DELETE RESTRICT,
    CONSTRAINT uq_div_ay UNIQUE (Div_Name, AY_ID)
);

-- 2. Teachers, Students & RBAC
CREATE TABLE Teachers (
    Emp_ID VARCHAR(20) PRIMARY KEY,
    Teacher_Name VARCHAR(100) NOT NULL,
    Designation VARCHAR(100) NOT NULL,
    Dept_ID VARCHAR(10) NOT NULL REFERENCES Departments(Dept_ID) ON DELETE RESTRICT,
    Qualification VARCHAR(100),
    Specialization VARCHAR(150),
    Date_Of_Joining DATE,
    Email VARCHAR(120) NOT NULL UNIQUE,
    Phone VARCHAR(20),
    Office_Room VARCHAR(50),
    Employment_Type VARCHAR(20) DEFAULT 'Permanent' CHECK (Employment_Type IN ('Permanent', 'Visiting', 'Ad-hoc')),
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'On Leave', 'Resigned')),
    Password_Hash VARCHAR(255) NOT NULL DEFAULT '$2b$12$e8yCjM7tE/s4w67P10qV2uFvjR1k9oZ...',
    Created_At TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Students (
    Student_ID VARCHAR(20) PRIMARY KEY,
    Roll_No VARCHAR(30) NOT NULL,
    Student_Name VARCHAR(100) NOT NULL,
    Div_ID VARCHAR(10) NOT NULL REFERENCES Divisions(Div_ID) ON DELETE RESTRICT,
    Program_ID VARCHAR(10) NOT NULL REFERENCES Programs(Program_ID) ON DELETE RESTRICT,
    Email VARCHAR(120) NOT NULL UNIQUE,
    Phone VARCHAR(20),
    Admission_Year INT NOT NULL,
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Detained', 'Transferred', 'Alumni')),
    Password_Hash VARCHAR(255) NOT NULL DEFAULT '$2b$12$e8yCjM7tE/s4w67P10qV2uFvjR1k9oZ...',
    Created_At TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_roll_division UNIQUE (Roll_No, Div_ID)
);

CREATE TABLE Roles (
    Role_ID VARCHAR(20) PRIMARY KEY,
    Role_Name VARCHAR(50) NOT NULL UNIQUE,
    Description TEXT
);

CREATE TABLE User_Role_Mappings (
    Mapping_ID SERIAL PRIMARY KEY,
    User_Identifier VARCHAR(20) NOT NULL,
    Role_ID VARCHAR(20) NOT NULL REFERENCES Roles(Role_ID) ON DELETE CASCADE,
    Assigned_At TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_role UNIQUE (User_Identifier, Role_ID)
);

-- 3. Courses & Allocations
CREATE TABLE Courses (
    Course_ID VARCHAR(10) PRIMARY KEY,
    Course_Code VARCHAR(20) NOT NULL UNIQUE,
    Course_Name VARCHAR(100) NOT NULL,
    Semester INT NOT NULL CHECK (Semester BETWEEN 1 AND 8),
    Dept_ID VARCHAR(10) NOT NULL REFERENCES Departments(Dept_ID) ON DELETE RESTRICT,
    Credits INT NOT NULL DEFAULT 4,
    Is_Elective BOOLEAN DEFAULT FALSE
);

CREATE TABLE Class_Teacher_Allocation (
    CT_Alloc_ID SERIAL PRIMARY KEY,
    Div_ID VARCHAR(10) NOT NULL REFERENCES Divisions(Div_ID) ON DELETE RESTRICT,
    Emp_ID VARCHAR(20) NOT NULL REFERENCES Teachers(Emp_ID) ON DELETE RESTRICT,
    AY_ID VARCHAR(10) NOT NULL REFERENCES Academic_Years(AY_ID) ON DELETE RESTRICT,
    From_Date DATE NOT NULL,
    To_Date DATE,
    Is_Active BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_ct_dates CHECK (To_Date IS NULL OR To_Date >= From_Date)
);

CREATE TABLE Course_Teacher_Allocation (
    CTA_ID SERIAL PRIMARY KEY,
    Course_ID VARCHAR(10) NOT NULL REFERENCES Courses(Course_ID) ON DELETE RESTRICT,
    Div_ID VARCHAR(10) NOT NULL REFERENCES Divisions(Div_ID) ON DELETE RESTRICT,
    Teacher_ID VARCHAR(20) NOT NULL REFERENCES Teachers(Emp_ID) ON DELETE RESTRICT,
    AY_ID VARCHAR(10) NOT NULL REFERENCES Academic_Years(AY_ID) ON DELETE RESTRICT,
    From_Date DATE NOT NULL,
    To_Date DATE,
    Is_Active BOOLEAN DEFAULT TRUE,
    CONSTRAINT chk_cta_dates CHECK (To_Date IS NULL OR To_Date >= From_Date)
);

-- 4. Teacher Guardians
CREATE TABLE Teacher_Guardians (
    TG_ID VARCHAR(10) PRIMARY KEY,
    Batch_Name VARCHAR(50) NOT NULL,
    Div_ID VARCHAR(10) NOT NULL REFERENCES Divisions(Div_ID) ON DELETE RESTRICT,
    AY_ID VARCHAR(10) NOT NULL REFERENCES Academic_Years(AY_ID) ON DELETE RESTRICT,
    Current_Teacher_ID VARCHAR(20) NOT NULL REFERENCES Teachers(Emp_ID) ON DELETE RESTRICT
);

CREATE TABLE TG_Student_Allocation (
    Alloc_ID VARCHAR(20) PRIMARY KEY,
    TG_ID VARCHAR(10) NOT NULL REFERENCES Teacher_Guardians(TG_ID) ON DELETE RESTRICT,
    Teacher_ID VARCHAR(20) NOT NULL REFERENCES Teachers(Emp_ID) ON DELETE RESTRICT,
    Student_ID VARCHAR(20) NOT NULL REFERENCES Students(Student_ID) ON DELETE RESTRICT,
    From_Date DATE NOT NULL,
    To_Date DATE,
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Transferred', 'Archived')),
    CONSTRAINT chk_tg_alloc_dates CHECK (To_Date IS NULL OR To_Date >= From_Date)
);

-- 5. Timetable Schedule & Sessions
CREATE TABLE Lecture_Schedule (
    Lecture_ID VARCHAR(20) PRIMARY KEY,
    Course_ID VARCHAR(10) NOT NULL REFERENCES Courses(Course_ID) ON DELETE RESTRICT,
    Div_ID VARCHAR(10) NOT NULL REFERENCES Divisions(Div_ID) ON DELETE RESTRICT,
    Teacher_ID VARCHAR(20) NOT NULL REFERENCES Teachers(Emp_ID) ON DELETE RESTRICT,
    Day_Of_Week VARCHAR(15) NOT NULL CHECK (Day_Of_Week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday')),
    Slot_No INT NOT NULL CHECK (Slot_No BETWEEN 1 AND 6),
    Start_Time TIME NOT NULL,
    End_Time TIME NOT NULL,
    Room_No VARCHAR(20) NOT NULL,
    Semester INT NOT NULL,
    AY_ID VARCHAR(10) NOT NULL REFERENCES Academic_Years(AY_ID) ON DELETE RESTRICT,
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Suspended')),
    CONSTRAINT chk_slot_time CHECK (End_Time > Start_Time),
    CONSTRAINT uq_div_day_slot UNIQUE (Div_ID, Day_Of_Week, Slot_No, AY_ID),
    CONSTRAINT uq_teacher_day_slot UNIQUE (Teacher_ID, Day_Of_Week, Slot_No, AY_ID),
    CONSTRAINT uq_room_day_slot UNIQUE (Room_No, Day_Of_Week, Slot_No, AY_ID)
);

CREATE TABLE Academic_Sessions (
    Session_ID BIGSERIAL PRIMARY KEY,
    Lecture_ID VARCHAR(20) NOT NULL REFERENCES Lecture_Schedule(Lecture_ID) ON DELETE RESTRICT,
    Session_Date DATE NOT NULL,
    Slot_No INT NOT NULL CHECK (Slot_No BETWEEN 1 AND 6),
    Course_ID VARCHAR(10) NOT NULL REFERENCES Courses(Course_ID) ON DELETE RESTRICT,
    Div_ID VARCHAR(10) NOT NULL REFERENCES Divisions(Div_ID) ON DELETE RESTRICT,
    Conducted_By_Teacher_ID VARCHAR(20) NOT NULL REFERENCES Teachers(Emp_ID) ON DELETE RESTRICT,
    Session_Status VARCHAR(20) DEFAULT 'Conducted' CHECK (Session_Status IN ('Conducted', 'Cancelled', 'Rescheduled')),
    Topics_Covered TEXT,
    Created_At TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_session_occurrence UNIQUE (Div_ID, Session_Date, Slot_No)
);

-- 6. Attendance & Audit
CREATE TABLE Attendance (
    Attendance_ID BIGSERIAL PRIMARY KEY,
    Session_ID BIGINT NOT NULL REFERENCES Academic_Sessions(Session_ID) ON DELETE CASCADE,
    Student_ID VARCHAR(20) NOT NULL REFERENCES Students(Student_ID) ON DELETE RESTRICT,
    Course_ID VARCHAR(10) NOT NULL REFERENCES Courses(Course_ID) ON DELETE RESTRICT,
    Attendance_Date DATE NOT NULL,
    Slot_No INT NOT NULL CHECK (Slot_No BETWEEN 1 AND 6),
    Status VARCHAR(20) NOT NULL CHECK (Status IN ('Present', 'Absent', 'Late', 'Excused')),
    Marked_By_Emp_ID VARCHAR(20) NOT NULL REFERENCES Teachers(Emp_ID) ON DELETE RESTRICT,
    Recorded_At TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    Last_Modified_At TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_slot_attendance UNIQUE (Student_ID, Course_ID, Attendance_Date, Slot_No),
    CONSTRAINT uq_session_student UNIQUE (Session_ID, Student_ID)
);

CREATE TABLE Attendance_Audit_Trail (
    Audit_ID BIGSERIAL PRIMARY KEY,
    Attendance_ID BIGINT NOT NULL REFERENCES Attendance(Attendance_ID) ON DELETE CASCADE,
    Old_Value VARCHAR(20) NOT NULL,
    New_Value VARCHAR(20) NOT NULL,
    Modified_By_Emp_ID VARCHAR(20) NOT NULL REFERENCES Teachers(Emp_ID) ON DELETE RESTRICT,
    Modification_Timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    Reason TEXT NOT NULL,
    IP_Address VARCHAR(45)
);

-- Indexes
CREATE INDEX idx_att_student_course ON Attendance(Student_ID, Course_ID);
CREATE INDEX idx_att_date ON Attendance(Attendance_Date);
CREATE INDEX idx_session_div_date ON Academic_Sessions(Div_ID, Session_Date);
CREATE INDEX idx_tg_student_alloc ON TG_Student_Allocation(Teacher_ID, Status);
CREATE INDEX idx_schedule_lookup ON Lecture_Schedule(Day_Of_Week, Slot_No, Teacher_ID);

-- Initial Reference Data
INSERT INTO Departments (Dept_ID, Dept_Name, Dept_Code) 
VALUES ('D01', 'Computer Science and Engineering', 'CSE');

INSERT INTO Academic_Years (AY_ID, AY_Name, Start_Date, End_Date, Is_Current)
VALUES ('AY2025', '2024-2025', '2024-07-01', '2025-06-30', TRUE);

INSERT INTO Programs (Program_ID, Program_Name, Program_Code, Dept_ID)
VALUES ('P01', 'B.Tech in Computer Science and Engineering', 'BTECH-CSE', 'D01');

INSERT INTO Classes (Class_ID, Class_Name, Year_Level, Program_ID)
VALUES 
    ('C01', 'Second Year CSE', 2, 'P01'),
    ('C02', 'Third Year CSE', 3, 'P01');

INSERT INTO Divisions (Div_ID, Div_Name, Class_ID, Room_No, AY_ID)
VALUES 
    ('DIV01', 'SY-A', 'C01', 'A-101', 'AY2025'),
    ('DIV02', 'SY-B', 'C01', 'A-102', 'AY2025'),
    ('DIV03', 'TY-A', 'C02', 'B-201', 'AY2025');

INSERT INTO Roles (Role_ID, Role_Name, Description)
VALUES
    ('HOD', 'Head of Department', 'Full department read-only monitoring and defaulter analytics'),
    ('CLASS_TEACHER', 'Class Teacher', 'Division-wide monitoring, reports, and division defaulters'),
    ('COURSE_TEACHER', 'Course Teacher', 'Slot-wise attendance entry and session management for taught courses'),
    ('TEACHER_GUARDIAN', 'Teacher Guardian', 'Mentorship and monitoring of allocated 20-student group'),
    ('STUDENT', 'Student', 'Individual personal attendance dashboard and warning alerts');
