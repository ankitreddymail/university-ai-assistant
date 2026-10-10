"""Script to validate student data integrity.

Ensures all student records have valid IDs, non-negative credits, GPA between 0.0 and 4.0,
and proper email formatting.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple


def validate_student_record(student: Dict[str, Any]) -> List[str]:
    """Validate a single student record dictionary against basic data rules."""
    errors = []
    student_id = student.get("student_id")
    if not student_id or not isinstance(student_id, str):
        errors.append("Invalid or missing student_id.")

    gpa = student.get("gpa")
    if gpa is None or not isinstance(gpa, (int, float)) or not (0.0 <= gpa <= 4.0):
        errors.append(f"Invalid GPA: {gpa}. Must be between 0.0 and 4.0.")

    credits_completed = student.get("credits_completed")
    if credits_completed is None or not isinstance(credits_completed, int) or credits_completed < 0:
        errors.append(f"Invalid credits: {credits_completed}. Must be non-negative integer.")

    email = student.get("email")
    if not email or "@" not in email:
        errors.append(f"Invalid email: {email}.")

    return errors


def validate_all_students(file_path: str = "data/students/students.json") -> bool:
    """Read student JSON file and validate every record."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: {file_path} not found.")
        return False

    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    all_valid = True
    for index, student in enumerate(records):
        errors = validate_student_record(student)
        if errors:
            all_valid = False
            print(f"Record {index} ({student.get('student_id')}) failed validation: {errors}")

    if all_valid:
        print(f"Validation successful: All {len(records)} records are valid.")
    return all_valid


if __name__ == "__main__":
    validate_all_students()
