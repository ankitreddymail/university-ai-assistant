"""Script to generate synthetic student test profiles.

Produces a JSON dataset containing diverse student scenarios (freshmen, graduating seniors,
students with holds, honors students, etc.) for validation and evaluation.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def generate_mock_students() -> List[Dict[str, Any]]:
    """Return a list of synthetic student records covering key test scenarios."""
    students = [
        {
            "student_id": "S1001",
            "full_name": "Aarav Sharma",
            "email": "aarav.sharma@campus.edu",
            "major": "Computer Science",
            "gpa": 3.85,
            "credits_completed": 124,
            "standing": "Senior",
            "holds": []
        },
        {
            "student_id": "S1002",
            "full_name": "Emily Chen",
            "email": "emily.chen@campus.edu",
            "major": "Mechanical Engineering",
            "gpa": 3.10,
            "credits_completed": 95,
            "standing": "Junior",
            "holds": ["library_fee"]
        },
        {
            "student_id": "S1003",
            "full_name": "Marcus Johnson",
            "email": "marcus.j@campus.edu",
            "major": "Business Administration",
            "gpa": 1.95,
            "credits_completed": 122,
            "standing": "Senior",
            "holds": []
        },
        {
            "student_id": "S1004",
            "full_name": "Priya Patel",
            "email": "priya.p@campus.edu",
            "major": "Data Science",
            "gpa": 3.92,
            "credits_completed": 60,
            "standing": "Sophomore",
            "holds": []
        },
        {
            "student_id": "S1005",
            "full_name": "David Kim",
            "email": "david.kim@campus.edu",
            "major": "Economics",
            "gpa": 2.80,
            "credits_completed": 118,
            "standing": "Senior",
            "holds": ["financial_aid_documents"]
        }
    ]
    return students


def save_students_to_json(students: List[Dict[str, Any]], output_path: str = "data/students/students.json") -> None:
    """Save generated student records to a formatted JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(students, f, indent=2)
    print(f"Generated and saved {len(students)} student profiles to {output_path}")


if __name__ == "__main__":
    records = generate_mock_students()
    save_students_to_json(records)
