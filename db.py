"""
db.py  –  Replaces MySQL with simple CSV file storage.
All other modules import from here instead of using mysql.connector.
"""

import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE  = os.path.join(BASE_DIR, "attendance_records", "students.csv")
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance_records", "attendance.csv")

STUDENT_FIELDS = [
    "student_id", "course", "dep", "year", "semester",
    "name", "division", "gender", "dob", "roll",
    "email", "phone", "address", "teacher", "photo_sample"
]

ATTENDANCE_FIELDS = [
    "attendance_id", "roll", "name", "dep", "time", "date", "status"
]

# ── ensure files exist with headers ──────────────────────────────────────────
def _ensure(filepath, fields):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        with open(filepath, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()

_ensure(STUDENTS_FILE,   STUDENT_FIELDS)
_ensure(ATTENDANCE_FILE, ATTENDANCE_FIELDS)


# ══ STUDENT CRUD ══════════════════════════════════════════════════════════════

def get_all_students():
    with open(STUDENTS_FILE, newline="") as f:
        return list(csv.DictReader(f))

def get_student_by_id(student_id):
    for s in get_all_students():
        if s["student_id"] == str(student_id):
            return s
    return None

def add_student(data: dict):
    students = get_all_students()
    # prevent duplicate IDs
    if any(s["student_id"] == data["student_id"] for s in students):
        raise ValueError(f"Student ID {data['student_id']} already exists.")
    students.append(data)
    _write_students(students)

def update_student(student_id, data: dict):
    students = get_all_students()
    for i, s in enumerate(students):
        if s["student_id"] == str(student_id):
            students[i] = data
            _write_students(students)
            return
    raise ValueError(f"Student ID {student_id} not found.")

def delete_student(student_id):
    students = [s for s in get_all_students()
                if s["student_id"] != str(student_id)]
    _write_students(students)

def _write_students(students):
    with open(STUDENTS_FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=STUDENT_FIELDS)
        w.writeheader()
        w.writerows(students)


# ══ ATTENDANCE ════════════════════════════════════════════════════════════════

def get_all_attendance():
    with open(ATTENDANCE_FILE, newline="") as f:
        return list(csv.DictReader(f))

def mark_attendance(student_id, roll, name, dep, status="Present"):
    from datetime import datetime
    records = get_all_attendance()
    today = datetime.now().strftime("%d/%m/%Y")

    # don't mark twice on same day
    already = any(
        r["roll"] == str(roll) and r["date"] == today
        for r in records
    )
    if already:
        return False

    new_id = str(len(records) + 1)
    now    = datetime.now().strftime("%H:%M:%S")
    record = {
        "attendance_id": new_id,
        "roll":          str(roll),
        "name":          str(name),
        "dep":           str(dep),
        "time":          now,
        "date":          today,
        "status":        status,
    }
    records.append(record)
    with open(ATTENDANCE_FILE, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=ATTENDANCE_FIELDS).writerow(record)
    return True
