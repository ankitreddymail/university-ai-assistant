"""Synthetic Student and Academic Data Generator (Annex C Compliant).

Generates realistic mock university records in CSV format conforming strictly to Annex C:
1. students: student_id, full_name, programme, batch_year, current_semester, cgpa, active_backlogs
2. courses: course_code, course_name, programme, semester, credits
3. attendance: student_id, course_code, classes_held, classes_attended
4. results: student_id, course_code, exam_session, exam_type, internal_marks, external_marks, total_marks, max_marks, result
5. rule_registry: rule_id, description, parameter, operator, value, scope_programmes, scope_batches, effective_from, effective_to, source_doc_id, source_section

SAFETY CONSTRAINTS:
- Never uses real student data.
- Student IDs S9000-S9999 and course codes starting with 'JDG' are strictly reserved for judges.
"""

import csv
import random
from pathlib import Path
from typing import Dict, Any

random.seed(42)

PROGRAMMES = [
    "B.Tech Computer Science and Engineering",
    "B.Tech Electronics and Communication Engineering",
]

BATCH_YEARS = [2021, 2022]

COURSES = [
    {
        "course_code": "CS301",
        "course_name": "Data Structures and Algorithms",
        "programme": "B.Tech Computer Science and Engineering",
        "semester": 3,
        "credits": 4,
    },
    {
        "course_code": "CS302",
        "course_name": "Operating Systems",
        "programme": "B.Tech Computer Science and Engineering",
        "semester": 4,
        "credits": 4,
    },
    {
        "course_code": "CS303",
        "course_name": "Database Management Systems",
        "programme": "B.Tech Computer Science and Engineering",
        "semester": 4,
        "credits": 4,
    },
    {
        "course_code": "EC201",
        "course_name": "Signals and Systems",
        "programme": "B.Tech Electronics and Communication Engineering",
        "semester": 3,
        "credits": 4,
    },
    {
        "course_code": "EC202",
        "course_name": "Digital Signal Processing",
        "programme": "B.Tech Electronics and Communication Engineering",
        "semester": 4,
        "credits": 4,
    },
    {
        "course_code": "EC203",
        "course_name": "Microprocessors and Microcontrollers",
        "programme": "B.Tech Electronics and Communication Engineering",
        "semester": 4,
        "credits": 4,
    },
]

RULES = [
    {
        "rule_id": "ATT_MIN_01",
        "description": "Minimum course attendance percentage required to sit for end-semester exams",
        "parameter": "min_attendance_percentage",
        "operator": ">=",
        "value": "75.0",
        "scope_programmes": "ALL",
        "scope_batches": "ALL",
        "effective_from": "2023-01-01",
        "effective_to": "2099-12-31",
        "source_doc_id": "academic_regulations_2024.pdf",
        "source_section": "Clause 4.1",
    },
    {
        "rule_id": "EXAM_PASS_01",
        "description": "Minimum total marks required to pass a registered course",
        "parameter": "min_total_marks",
        "operator": ">=",
        "value": "40.0",
        "scope_programmes": "ALL",
        "scope_batches": "ALL",
        "effective_from": "2023-01-01",
        "effective_to": "2099-12-31",
        "source_doc_id": "academic_regulations_2024.pdf",
        "source_section": "Clause 6.2",
    },
    {
        "rule_id": "SUPP_EXAM_01",
        "description": "Maximum active backlogs allowed to sit for supplementary exams",
        "parameter": "max_backlogs_allowed",
        "operator": "<=",
        "value": "3",
        "scope_programmes": "ALL",
        "scope_batches": "ALL",
        "effective_from": "2023-01-01",
        "effective_to": "2099-12-31",
        "source_doc_id": "academic_regulations_2024.pdf",
        "source_section": "Clause 7.4",
    },
    {
        "rule_id": "PLACE_CGPA_01",
        "description": "Minimum CGPA required to participate in campus placement recruitment",
        "parameter": "min_cgpa",
        "operator": ">=",
        "value": "6.5",
        "scope_programmes": "ALL",
        "scope_batches": "ALL",
        "effective_from": "2023-01-01",
        "effective_to": "2099-12-31",
        "source_doc_id": "placement_policy_2024.pdf",
        "source_section": "Clause 3.1",
    },
    {
        "rule_id": "PLACE_BACKLOG_01",
        "description": "Maximum active backlogs permitted for placement participation",
        "parameter": "max_active_backlogs",
        "operator": "==",
        "value": "0",
        "scope_programmes": "ALL",
        "scope_batches": "ALL",
        "effective_from": "2023-01-01",
        "effective_to": "2099-12-31",
        "source_doc_id": "placement_policy_2024.pdf",
        "source_section": "Clause 3.2",
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
    """Generate all Annex C CSV files."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Generate 35 students (S1001 - S1035)
    students = []
    for i in range(1, 36):
        student_id = f"S{1000 + i}"
        first = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        last = LAST_NAMES[(i - 1) % len(LAST_NAMES)]
        full_name = f"{first} {last}"
        prog = PROGRAMMES[i % len(PROGRAMMES)]
        batch_year = BATCH_YEARS[i % len(BATCH_YEARS)]
        current_semester = 6 if batch_year == 2021 else 4
        cgpa = round(random.uniform(5.5, 9.8), 2)
        active_backlogs = 1 if i in (3, 12) else 0

        students.append({
            "student_id": student_id,
            "full_name": full_name,
            "programme": prog,
            "batch_year": batch_year,
            "current_semester": current_semester,
            "cgpa": cgpa,
            "active_backlogs": active_backlogs,
            "email": f"{first.lower()}.{last.lower()}{i}@campus.edu",
            "holds": "library_fine" if i in (4, 17) else ("tuition_fee_pending" if i == 9 else ""),
        })

    # Save students.csv
    students_csv = out_path / "students.csv"
    with open(students_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "student_id", "full_name", "programme", "batch_year",
            "current_semester", "cgpa", "active_backlogs", "email", "holds"
        ])
        writer.writeheader()
        writer.writerows(students)

    # Save courses.csv
    courses_csv = out_path / "courses.csv"
    with open(courses_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "course_code", "course_name", "programme", "semester", "credits"
        ])
        writer.writeheader()
        writer.writerows(COURSES)

    # 2. Generate attendance records (classes_held, classes_attended)
    attendance_records = []
    for s in students:
        s_prog = s["programme"]
        prog_courses = [c for c in COURSES if c["programme"] == s_prog]
        for c in prog_courses:
            classes_held = 40
            # Some students have shortage (< 75% i.e. < 30 classes)
            if s["student_id"] in ("S1002", "S1015", "S1028"):
                classes_attended = random.randint(22, 28)
            else:
                classes_attended = random.randint(31, 39)

            attendance_records.append({
                "student_id": s["student_id"],
                "course_code": c["course_code"],
                "classes_held": classes_held,
                "classes_attended": classes_attended,
            })

    attendance_csv = out_path / "attendance.csv"
    with open(attendance_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "student_id", "course_code", "classes_held", "classes_attended"
        ])
        writer.writeheader()
        writer.writerows(attendance_records)

    # 3. Generate results records
    results_records = []
    for s in students:
        s_prog = s["programme"]
        prog_courses = [c for c in COURSES if c["programme"] == s_prog]
        for c in prog_courses:
            session = "Apr-May 2024" if c["semester"] == 4 else "Nov-Dec 2023"
            if s["student_id"] in ("S1003", "S1012") and c["course_code"] in ("CS301", "EC201"):
                internal = 12.0
                external = 20.0
                total = internal + external
                result = "Fail"
            else:
                internal = round(random.uniform(28.0, 38.0), 1)
                external = round(random.uniform(40.0, 56.0), 1)
                total = internal + external
                result = "Pass"

            results_records.append({
                "student_id": s["student_id"],
                "course_code": c["course_code"],
                "exam_session": session,
                "exam_type": "Regular",
                "internal_marks": internal,
                "external_marks": external,
                "total_marks": total,
                "max_marks": 100.0,
                "result": result,
            })

    results_csv = out_path / "results.csv"
    with open(results_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "student_id", "course_code", "exam_session", "exam_type",
            "internal_marks", "external_marks", "total_marks", "max_marks", "result"
        ])
        writer.writeheader()
        writer.writerows(results_records)

    # 4. Save rule_registry.csv
    rules_csv = out_path / "rule_registry.csv"
    with open(rules_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rule_id", "description", "parameter", "operator", "value",
            "scope_programmes", "scope_batches", "effective_from", "effective_to",
            "source_doc_id", "source_section"
        ])
        writer.writeheader()
        writer.writerows(RULES)

    counts = {
        "students": len(students),
        "courses": len(COURSES),
        "programmes": len(PROGRAMMES),
        "batches": len(BATCH_YEARS),
        "attendance": len(attendance_records),
        "results": len(results_records),
        "rules": len(RULES),
    }
    print(f"Generated Annex C CSV datasets in {output_dir}:")
    for k, v in counts.items():
        print(f"  - {k}: {v}")
    return counts


if __name__ == "__main__":
    generate_synthetic_data()
