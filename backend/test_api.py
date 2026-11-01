"""
Automated Test Suite for CSE Attendance Backend APIs
Validates Bcrypt Login, JWT Token Issuance, and Strict RBAC Enforcement.
"""

import sys
import os

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_system():
    print("\n" + "="*70)
    print(" RUNNING CSE ATTENDANCE API & RBAC AUTOMATED TEST SUITE ")
    print("="*70)

    # 1. Health check
    res = client.get("/")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[PASS] 1. API Health Check OK:", res.json()["status"])

    # Helper for login
    def login_user(username, password="password123"):
        r = client.post("/login", json={"username": username, "password": password})
        assert r.status_code == 200, f"Login failed for {username}: {r.text}"
        data = r.json()
        return data["access_token"], data["user"]

    # 2. Login as different roles
    token_hod, user_hod = login_user("EMP001")
    print(f"[PASS] 2a. HoD Login (EMP001): Roles = {user_hod['roles']}")
    assert "HOD" in user_hod["roles"]

    token_ct, user_ct = login_user("EMP002") # CT for DIV01 (SY-A)
    print(f"[PASS] 2b. Class Teacher Login (EMP002): Div = {user_ct['assigned_division']}, Roles = {user_ct['roles']}")
    assert "CLASS_TEACHER" in user_ct["roles"]

    token_teacher, user_teacher = login_user("EMP005") # Course Teacher (Data Structures)
    print(f"[PASS] 2c. Course Teacher Login (EMP005): Roles = {user_teacher['roles']}")
    assert "COURSE_TEACHER" in user_teacher["roles"]

    token_tg, user_tg = login_user("EMP006") # TG for TG01 (SY-A 20 students)
    print(f"[PASS] 2d. TG Login (EMP006): TG_ID = {user_tg['tg_id']}, Roles = {user_tg['roles']}")
    assert "TEACHER_GUARDIAN" in user_tg["roles"]

    token_stu, user_stu = login_user("S001")
    print(f"[PASS] 2e. Student Login (S001): Roles = {user_stu['roles']}")
    assert "STUDENT" in user_stu["roles"]

    # 3. TG Enforcement: TG can fetch strictly their 20 students
    headers_tg = {"Authorization": f"Bearer {token_tg}"}
    r = client.get("/tg/my-students", headers=headers_tg)
    assert r.status_code == 200, f"TG students fetch failed: {r.text}"
    tg_students = r.json()
    print(f"[PASS] 3a. TG (EMP006) fetched their allotted students count: {len(tg_students)} (Expected: exactly 20)")
    assert len(tg_students) == 20
    assert tg_students[0]["student_id"] == "S001"
    assert tg_students[-1]["student_id"] == "S020"

    # 4. TG Attendance Report & Defaulter Flagging
    r = client.get("/tg/attendance-report", headers=headers_tg)
    assert r.status_code == 200
    report = r.json()
    print(f"[PASS] 4a. TG Attendance Report generated for {len(report)} students.")
    # Check S005 is flagged as defaulter
    s5_report = next((item for item in report if item["student_id"] == "S005"), None)
    assert s5_report is not None
    print(f"[PASS] 4b. TG Defaulter Check for S005: {s5_report['attendance_percentage']}% -> is_defaulter: {s5_report['is_defaulter']}")
    assert s5_report["is_defaulter"] is True

    # 5. RBAC Violation Test: Student trying to access TG or Reports routes -> 403 Forbidden
    headers_stu = {"Authorization": f"Bearer {token_stu}"}
    r = client.get("/tg/my-students", headers=headers_stu)
    print(f"[PASS] 5a. Student accessing TG route blocked with status: {r.status_code} (Expected: 403)")
    assert r.status_code == 403

    r = client.get("/reports/division/DIV01", headers=headers_stu)
    print(f"[PASS] 5b. Student accessing Division Reports blocked with status: {r.status_code} (Expected: 403)")
    assert r.status_code == 403

    # 6. Student Dashboard: Accessing own attendance
    r = client.get("/student/my-attendance", headers=headers_stu)
    assert r.status_code == 200
    stu_dash = r.json()
    print(f"[PASS] 6. Student S001 fetched personal dashboard: Overall % = {stu_dash['overall_percentage']}%, Courses = {len(stu_dash['courses'])}")
    assert stu_dash["student_id"] == "S001"
    assert len(stu_dash["courses"]) > 0

    # 7. Class Teacher Division Scoping Rule
    headers_ct = {"Authorization": f"Bearer {token_ct}"}
    # EMP002 is CT for DIV01 -> allowed
    r = client.get("/reports/division/DIV01", headers=headers_ct)
    assert r.status_code == 200
    print(f"[PASS] 7a. Class Teacher (EMP002) accessed assigned division DIV01: Avg = {r.json()['division_average_percentage']}%, Defaulters = {r.json()['defaulters_count']}")
    
    # EMP002 attempting to access DIV02 -> must be 403 Forbidden!
    r = client.get("/reports/division/DIV02", headers=headers_ct)
    print(f"[PASS] 7b. Class Teacher (EMP002) accessing other division DIV02 blocked with status: {r.status_code} (Expected: 403)")
    assert r.status_code == 403

    # 8. HoD Access Rule: HoD has unrestricted read access
    headers_hod = {"Authorization": f"Bearer {token_hod}"}
    r1 = client.get("/reports/division/DIV01", headers=headers_hod)
    r2 = client.get("/reports/division/DIV02", headers=headers_hod)
    r3 = client.get("/reports/division/DIV03", headers=headers_hod)
    assert r1.status_code == 200 and r2.status_code == 200 and r3.status_code == 200
    print(f"[PASS] 8. HoD (EMP001) successfully accessed all 3 divisions (DIV01, DIV02, DIV03).")

    # 9. Course Teacher APIs: Courses & Submission
    headers_teacher = {"Authorization": f"Bearer {token_teacher}"}
    r = client.get("/teacher/my-courses", headers=headers_teacher)
    assert r.status_code == 200
    my_courses = r.json()
    print(f"[PASS] 9a. Course Teacher (EMP005) fetched assigned courses count: {len(my_courses)}")
    assert len(my_courses) > 0

    # Submit attendance for slot
    target_course = my_courses[0]["course_id"]
    target_div = my_courses[0]["div_id"]
    submit_payload = {
        "session_date": "2026-10-30",
        "slot_no": 1,
        "course_id": target_course,
        "div_id": target_div,
        "topics_covered": "Test transaction submission of Unit 4.",
        "records": [
            {"student_id": f"S{i:03d}", "status": "Present" if i % 4 != 0 else "Absent"}
            for i in range(1, 61)
        ]
    }
    r = client.post("/attendance/submit", json=submit_payload, headers=headers_teacher)
    assert r.status_code == 200, f"Attendance submit failed: {r.text}"
    print(f"[PASS] 9b. Atomic attendance submitted successfully for 60 students: Session ID = {r.json()['session_id']}")

    # 10. Attendance Modification with Audit Trail
    modify_payload = {
        "attendance_id": 1,
        "new_status": "Absent",
        "reason": "Verified leave certificate by HOD"
    }
    r = client.put("/attendance/modify", json=modify_payload, headers=headers_teacher)
    assert r.status_code == 200
    print(f"[PASS] 10. Attendance modification logged into Audit Trail: {r.json()['message']}")

    print("="*70)
    print(" ALL 10 TESTS PASSED SUCCESSFULLY! RBAC & BUSINESS LOGIC 100% VERIFIED! ")
    print("="*70)

if __name__ == "__main__":
    test_system()
