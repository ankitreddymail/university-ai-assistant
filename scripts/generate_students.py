"""Synthetic Student and Academic Data Generator (Annex C).

Generates realistic mock university records in CSV format:
- 35 synthetic students across 2 programmes and 2 admission batches
- CGPA on a 0.0 - 10.0 scale
- 6 academic courses
- Attendance records
- Semester results and grades
- Rule registry entries linking criteria to source documents and clauses

STRICT SAFETY CONSTRAINTS:
- Never uses real student data.
- Student IDs S9000-S9999 and course codes starting with 'JDG' are reserved for judges.
"""

import csv
import random
from pathlib import Path
from typing import List, Dict, Any

# Fix seed for reproducible test datasets
random.seed(42)

PROGRAMMES = [
    "B.Tech Computer Science and Engineering",
    "B.Tech Electronics and Communication Engineering",
]

BATCHES = [
    "2021-2025",
    "2022-2026",
]

COURSES = [
    {
        "course_code": "CS301",
        "course_name": "Data Structures and Algorithms",
        "programme": "B.Tech Computer Science and Engineering",
        "semester": 3,
        "credits": 4,
        "instructor": "Dr. Arvind Rao",
    },
    {
        "course_code": "CS302",
        "course_name": "Operating Systems",
        "programme": "B.Tech Computer Science and Engineering",
        "semester": 4,
        "credits": 4,
        "instructor": "Prof. Priya Nair",
    },
    {
        "course_code": "CS303",
        "course_name": "Database Management Systems",
        "programme": "B.Tech Computer Science and Engineering",
        "semester": 4,
        "credits": 4,
        "instructor": "Dr. Sanjay Gupta",
    },
    {
        "course_code": "EC201",
        "course_name": "Signals and Systems",
        "programme": "B.Tech Electronics and Communication Engineering",
        "semester": 3,
        "credits": 4,
        "instructor": "Dr. Meenakshi Sundaram",
    },
    {
        "course_code": "EC202",
        "course_name": "Digital Signal Processing",
        "programme": "B.Tech Electronics and Communication Engineering",
        "semester": 4,
        "credits": 4,
        "instructor": "Prof. Rajesh Kumar",
    },
    {
        "course_code": "EC203",
        "course_name": "Microprocessors and Microcontrollers",
        "programme": "B.Tech Electronics and Communication Engineering",
        "semester": 4,
        "credits": 4,
        "instructor": "Dr. Anita Desai",
    },
]

RULES = [
    {
        "rule_id": "ATT_MIN_01",
        "rule_category": "attendance",
        "description": "Minimum course attendance required to sit for end-semester exams",
        "parameter_name": "min_attendance_percentage",
        "parameter_value": "75.0",
        "source_document": "academic_regulations_2024.pdf",
        "clause": "Clause 4.1",
    },
    {
        "rule_id": "EXAM_PASS_01",
        "rule_category": "exam_result",
        "description": "Course clearance requires grade points greater than or equal to 4.0",
        "parameter_name": "min_grade_points",
        "parameter_value": "4.0",
        "source_document": "academic_regulations_2024.pdf",
        "clause": "Clause 6.2",
    },
    {
        "rule_id": "SUPP_EXAM_01",
        "rule_category": "supplementary_exam",
        "description": "Maximum number of backlogs allowed to sit for supplementary exams",
        "parameter_name": "max_backlogs_allowed",
        "parameter_value": "3",
        "source_document": "academic_regulations_2024.pdf",
        "clause": "Clause 7.4",
    },
    {
        "rule_id": "PLACE_CGPA_01",
        "rule_category": "placement",
        "description": "Minimum CGPA required to participate in campus placement recruitment",
        "parameter_name": "min_cgpa",
        "parameter_value": "6.5",
        "source_document": "placement_policy_2024.pdf",
        "clause": "Clause 3.1",
    },
    {
        "rule_id": "PLACE_BACKLOG_01",
        "rule_category": "placement",
        "description": "Maximum active backlogs permitted for placement participation",
        "parameter_name": "max_active_backlogs",
        "parameter_value": "0",
        "source_document": "placement_policy_2024.pdf",
        "clause": "Clause 3.2",
    },
]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna",
    "Ishaan", "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Chiara", "Riya", "Anushka",
    "Navya", "Sneha", "Kavya", "Tanvi", "Rohan", "Vikram", "Neha", "Rahul", "Pooja",
    "Karthik", "Deepak", "Swati", "Nikhil", "Gaurav", "Suresh", "Manish", "Divya"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Rao", "Nair", "Iyer", "Kumar", "Singh",
    "Das", "Chowdhury", "Banerjee", "Bose", "Joshi", "Kulkarni", "Deshmukh", "Pillai",
    "Menon", "Bhat", "Hegde", "Mehta", "Shah", "Kapoor", "Malhotra", "Saxena",
    "Gupta", "Mishra", "Pandey", "Tripathi", "Trivedi", "Shukla", "Dubey", "Yadav"
]


def generate_synthetic_data(output_dir: str = "data/students") -> Dict[str, int]:
    """Generate all CSV files for students, courses, attendance, results, and rules."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Generate 35 students (S1001 - S1035)
    students = []
    for i in range(1, 36):
        student_id = f"S{1000 + i}"
        first = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        last = LAST_NAMES[(i - 1) % len(LAST_NAMES)]
        full_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@campus.edu"
        prog = PROGRAMMES[i % len(PROGRAMMES)]
        batch = BATCHES[i % len(BATCHES)]
        sem = 6 if batch == "2021-2025" else 4
        # CGPA on 0-10 scale (between 5.5 and 9.8)
        cgpa = round(random.uniform(5.5, 9.8), 2)
        standing = "Good Standing" if cgpa >= 6.0 else "Academic Probation"
        holds = "library_fine" if i in (4, 17) else ("tuition_fee_pending" if i == 9 else "")

        students.append({
            "student_id": student_id,
            "full_name": full_name,
            "email": email,
            "programme": prog,
            "batch": batch,
            "current_semester": sem,
            "cgpa": cgpa,
            "standing": standing,
            "holds": holds,
        })

    # Save students.csv
    students_csv = out_path / "students.csv"
    with open(students_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "student_id", "full_name", "email", "programme", "batch",
            "current_semester", "cgpa", "standing", "holds"
        ])
        writer.writeheader()
        writer.writerows(students)

    # Save courses.csv
    courses_csv = out_path / "courses.csv"
    with open(courses_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "course_code", "course_name", "programme", "semester", "credits", "instructor"
        ])
        writer.writeheader()
        writer.writerows(COURSES)

    # 2. Generate attendance records
    attendance_records = []
    for s in students:
        s_prog = s["programme"]
        # Match student's programme courses
        prog_courses = [c for c in COURSES if c["programme"] == s_prog]
        for c in prog_courses:
            total_classes = 40
            # Some students have short attendance (< 75%) to test eligibility
            if s["student_id"] in ("S1002", "S1015", "S1028"):
                attended = random.randint(22, 28)
            else:
                attended = random.randint(31, 39)
            pct = round((attended / total_classes) * 100, 1)
            attendance_records.append({
                "student_id": s["student_id"],
                "course_code": c["course_code"],
                "classes_attended": attended,
                "total_classes": total_classes,
                "attendance_percentage": pct,
            })

    attendance_csv = out_path / "attendance.csv"
    with open(attendance_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "student_id", "course_code", "classes_attended", "total_classes", "attendance_percentage"
        ])
        writer.writeheader()
        writer.writerows(attendance_records)

    # 3. Generate exam results
    results_records = []
    for s in students:
        s_prog = s["programme"]
        prog_courses = [c for c in COURSES if c["programme"] == s_prog]
        for c in prog_courses:
            # S1003, S1012 have backlogs
            if s["student_id"] in ("S1003", "S1012") and c["course_code"] in ("CS301", "EC201"):
                grade = "F"
                grade_pts = 0.0
                status = "Fail"
            else:
                grade = random.choice(["A", "A+", "B", "B+"])
                grade_pts = 9.0 if "A" in grade else 7.5
                status = "Pass"

            results_records.append({
                "student_id": s["student_id"],
                "course_code": c["course_code"],
                "semester": c["semester"],
                "grade": grade,
                "grade_points": grade_pts,
                "credits": c["credits"],
                "status": status,
            })

    results_csv = out_path / "results.csv"
    with open(results_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "student_id", "course_code", "semester", "grade", "grade_points", "credits", "status"
        ])
        writer.writeheader()
        writer.writerows(results_records)

    # 4. Save rule_registry.csv
    rules_csv = out_path / "rule_registry.csv"
    with open(rules_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rule_id", "rule_category", "description", "parameter_name",
            "parameter_value", "source_document", "clause"
        ])
        writer.writeheader()
        writer.writerows(RULES)

    counts = {
        "students": len(students),
        "courses": len(COURSES),
        "programmes": len(PROGRAMMES),
        "batches": len(BATCHES),
        "attendance": len(attendance_records),
        "results": len(results_records),
        "rules": len(RULES),
    }
    print(f"Generated synthetic CSV datasets in {output_dir}:")
    for k, v in counts.items():
        print(f"  - {k}: {v}")
    return counts


if __name__ == "__main__":
    generate_synthetic_data()
