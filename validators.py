"""
validators.py  —  Central validation helpers for the Face Recognition System.
Import and call these from any module to get consistent, friendly error messages.
"""

import re
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════════════
#  STUDENT VALIDATORS
# ══════════════════════════════════════════════════════════════════════════════

def validate_student(data: dict) -> list[str]:
    """
    Validate all student fields.
    Returns a list of error strings (empty list = all good).
    """
    errors = []

    sid  = data.get("student_id", "").strip()
    name = data.get("name", "").strip()
    roll = data.get("roll", "").strip()

    # ── required fields ───────────────────────────────────────────────────────
    if not sid:
        errors.append("Student ID is required.")
    if not name:
        errors.append("Student Name is required.")
    if not roll:
        errors.append("Roll Number is required.")

    # ── Student ID: alphanumeric + dashes/underscores, 2–30 chars ─────────────
    if sid and not re.fullmatch(r"[A-Za-z0-9_\-]{2,30}", sid):
        errors.append(
            "Student ID must be 2–30 characters and contain only letters, "
            "digits, hyphens (-), or underscores (_).\n"
            "  Example: 2022-CE-5  or  STU001"
        )

    # ── Roll Number: integers ONLY ─────────────────────────────────────────────
    if roll:
        if not roll.isdigit():
            errors.append(
                "Roll Number must be a whole number (digits only).\n"
                "  ✗ Wrong:  'A12'  '12.5'  'roll12'\n"
                "  ✓ Correct: '12'  '101'"
            )
        elif not (1 <= int(roll) <= 9999):
            errors.append("Roll Number must be between 1 and 9999.")

    # ── Name: letters + spaces only ───────────────────────────────────────────
    if name and not re.fullmatch(r"[A-Za-z ]{2,60}", name):
        errors.append(
            "Name must be 2–60 characters and contain only letters and spaces."
        )

    # ── Email (optional but validated if present) ─────────────────────────────
    email = data.get("email", "").strip()
    if email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append("Email address format is invalid.  Example: user@example.com")

    # ── Phone: digits, optional leading +, 7–15 chars ─────────────────────────
    phone = data.get("phone", "").strip()
    if phone and not re.fullmatch(r"\+?\d{7,15}", phone):
        errors.append(
            "Phone number must be 7–15 digits (optional leading +).\n"
            "  Example: 03001234567  or  +923001234567"
        )

    # ── Date of Birth: DD/MM/YYYY, not in the future, age 5–100 ──────────────
    dob = data.get("dob", "").strip()
    if dob:
        try:
            dt = datetime.strptime(dob, "%d/%m/%Y")
            age = (datetime.now() - dt).days // 365
            if age < 5 or age > 100:
                errors.append("Date of Birth seems incorrect (age must be 5–100 years).")
            if dt > datetime.now():
                errors.append("Date of Birth cannot be in the future.")
        except ValueError:
            errors.append(
                "Date of Birth must be in DD/MM/YYYY format.\n"
                "  Example: 15/08/2002"
            )

    # ── Teacher / Address: no empty-looking whitespace-only strings ───────────
    teacher = data.get("teacher", "").strip()
    if teacher and len(teacher) < 2:
        errors.append("Teacher name must be at least 2 characters.")

    return errors


# ══════════════════════════════════════════════════════════════════════════════
#  ATTENDANCE VALIDATORS  (for manual-entry screens if added later)
# ══════════════════════════════════════════════════════════════════════════════

def validate_attendance_roll(roll: str) -> str | None:
    """
    Validate a roll number entered manually.
    Returns an error string, or None if valid.
    """
    roll = roll.strip()
    if not roll:
        return "Roll Number cannot be empty."
    if not roll.isdigit():
        return (
            "Roll Number must contain digits only.\n"
            "  ✗ Wrong:  'A12'  '12a'\n"
            "  ✓ Correct: '12'  '101'"
        )
    if not (1 <= int(roll) <= 9999):
        return "Roll Number must be between 1 and 9999."
    return None


def validate_student_id(sid: str) -> str | None:
    """
    Validate a student ID string.
    Returns an error string, or None if valid.
    """
    sid = sid.strip()
    if not sid:
        return "Student ID cannot be empty."
    if not re.fullmatch(r"[A-Za-z0-9_\-]{2,30}", sid):
        return (
            "Student ID must be 2–30 characters and contain only\n"
            "letters, digits, hyphens (-), or underscores (_).\n"
            "  Example: 2022-CE-5  or  STU001"
        )
    return None


def validate_search_term(term: str) -> str | None:
    """Allow letters, digits, spaces, hyphens. Reject SQL/script injection."""
    if not term.strip():
        return "Search term cannot be empty."
    if re.search(r"[;'\"\\<>]", term):
        return "Search term contains invalid characters."
    return None
