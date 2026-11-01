# Centralized Attendance Management & Monitoring System - Database Setup Guide

This guide details the complete database setup, Docker environment, CSV data ingestion, and testing pipeline for the CSE Department Attendance System.

---

## 1. Quick Start with Docker (PostgreSQL + pgAdmin + Adminer)

### Prerequisites
- Docker & Docker Compose installed.

### Commands
```bash
# 1. Start PostgreSQL 16, pgAdmin 4, and Adminer in the background
docker compose up -d

# 2. Ingest CSV data and generate 2 weeks of dummy attendance into PostgreSQL
python seed_data.py
```

### Web GUI Access Points
| Tool | URL | Credentials | Notes |
| :--- | :--- | :--- | :--- |
| **pgAdmin 4** | `http://localhost:5050` | Email: `admin@inst.edu`<br>Password: `admin` | Auto-connected to `attendance_db` via `pgadmin_servers.json` |
| **Adminer** | `http://localhost:8080` | System: `PostgreSQL`<br>Server: `attendance_db`<br>Username: `postgres`<br>Password: `postgres`<br>Database: `cse_attendance` | Ultra-lightweight web database browser |

---

## 2. Instant Local SQLite Mode (Zero Docker Required)

If Docker is not running or you want instant local testing, `seed_data.py` comes with native SQLite support:

```bash
# Creates and seeds local cse_attendance.db with all 17 tables and 10,000+ attendance records
python seed_data.py --sqlite
```

---

## 3. Seeded Database Content Summary

| Table Name | Row Count | Description |
| :--- | :---: | :--- |
| `departments` | 1 | CSE Department (`D01`) |
| `programs` | 1 | B.Tech Computer Science & Engineering (`P01`) |
| `classes` | 2 | Second Year (`C01`) and Third Year (`C02`) |
| `divisions` | 3 | `DIV01` (SY-A), `DIV02` (SY-B), `DIV03` (TY-A) |
| `teachers` | 14 | Faculty `EMP001` to `EMP014` |
| `roles` | 5 | `HOD`, `CLASS_TEACHER`, `COURSE_TEACHER`, `TEACHER_GUARDIAN`, `STUDENT` |
| `user_role_mappings` | 198 | Multi-role assignments for all faculty and students |
| `students` | 180 | 60 students per division (`S001` to `S180`) |
| `courses` | 12 | 6 SY subjects (`CR01`-`CR06`) + 6 TY subjects (`CR07`-`CR12`) |
| `class_teacher_allocation` | 3 | `EMP002` (SY-A), `EMP003` (SY-B), `EMP004` (TY-A) |
| `course_teacher_allocation` | 18 | Teacher-to-Course-Division assignments |
| `teacher_guardians` | 9 | Mentorship groups `TG01` to `TG09` |
| `tg_student_allocation` | 180 | **Strict 20-student allocation per TG** |
| `lecture_schedule` | 90 | Mon–Fri timetable (6 slots × 3 divisions = 90 slots/week) |
| `academic_sessions` | 180 | Actual sessions over past 2 weeks (10 working days) |
| `attendance` | 10,140 | Student slot-wise attendance records |
| `attendance_audit_trail` | 3 | Sample audited attendance corrections |

---

## 4. Verification Queries

### Check Defaulter Students (< 75% Attendance)
```sql
SELECT 
    s.student_id, 
    s.student_name, 
    s.div_id, 
    COUNT(a.attendance_id) AS total_sessions,
    SUM(CASE WHEN a.status IN ('Present', 'Late') THEN 1 ELSE 0 END) AS attended_sessions,
    ROUND(100.0 * SUM(CASE WHEN a.status IN ('Present', 'Late') THEN 1 ELSE 0 END) / COUNT(a.attendance_id), 2) AS attendance_pct
FROM students s
JOIN attendance a ON s.student_id = a.student_id
GROUP BY s.student_id, s.student_name, s.div_id
HAVING ROUND(100.0 * SUM(CASE WHEN a.status IN ('Present', 'Late') THEN 1 ELSE 0 END) / COUNT(a.attendance_id), 2) < 75.0
ORDER BY attendance_pct ASC;
```

### Check TG Group Attendance (e.g. TG01 - EMP006)
```sql
SELECT 
    tga.tg_id,
    tga.teacher_id AS tg_faculty_id,
    s.student_id,
    s.roll_no,
    s.student_name,
    COUNT(a.attendance_id) AS total_lectures,
    ROUND(100.0 * SUM(CASE WHEN a.status IN ('Present', 'Late') THEN 1 ELSE 0 END) / COUNT(a.attendance_id), 2) AS attendance_pct
FROM tg_student_allocation tga
JOIN students s ON tga.student_id = s.student_id
JOIN attendance a ON s.student_id = a.student_id
WHERE tga.teacher_id = 'EMP006' AND tga.status = 'Active'
GROUP BY tga.tg_id, tga.teacher_id, s.student_id, s.roll_no, s.student_name
ORDER BY attendance_pct ASC;
```
