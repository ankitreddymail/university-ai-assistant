"""Script to initialize SQLite database and load synthetic student records from CSV.

Initializes the required SQLite tables:
- students
- courses
- attendance
- results
- rule_registry

And imports data from CSV files in data/students/ into university.db.
"""

import csv
import sqlite3
from pathlib import Path
from typing import Dict, Any


def init_db(db_path: str) -> None:
    """Create all 5 required SQLite tables according to Annex C schema."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Drop old tables if upgrading schema
        cursor.execute("DROP TABLE IF EXISTS attendance;")
        cursor.execute("DROP TABLE IF EXISTS results;")
        cursor.execute("DROP TABLE IF EXISTS courses;")
        cursor.execute("DROP TABLE IF EXISTS students;")
        cursor.execute("DROP TABLE IF EXISTS rule_registry;")

        # 1. students table
        cursor.execute("""
            CREATE TABLE students (
                student_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                programme TEXT NOT NULL,
                batch TEXT NOT NULL,
                current_semester INTEGER NOT NULL,
                cgpa REAL NOT NULL,
                standing TEXT NOT NULL,
                holds TEXT DEFAULT ''
            );
        """)

        # 2. courses table
        cursor.execute("""
            CREATE TABLE courses (
                course_code TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                programme TEXT NOT NULL,
                semester INTEGER NOT NULL,
                credits INTEGER NOT NULL,
                instructor TEXT NOT NULL
            );
        """)

        # 3. attendance table
        cursor.execute("""
            CREATE TABLE attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_code TEXT NOT NULL,
                classes_attended INTEGER NOT NULL,
                total_classes INTEGER NOT NULL,
                attendance_percentage REAL NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_code) REFERENCES courses(course_code)
            );
        """)

        # 4. results table
        cursor.execute("""
            CREATE TABLE results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_code TEXT NOT NULL,
                semester INTEGER NOT NULL,
                grade TEXT NOT NULL,
                grade_points REAL NOT NULL,
                credits INTEGER NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_code) REFERENCES courses(course_code)
            );
        """)

        # 5. rule_registry table
        cursor.execute("""
            CREATE TABLE rule_registry (
                rule_id TEXT PRIMARY KEY,
                rule_category TEXT NOT NULL,
                description TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                parameter_value TEXT NOT NULL,
                source_document TEXT NOT NULL,
                clause TEXT NOT NULL
            );
        """)

        conn.commit()
    finally:
        conn.close()


def load_csv_data(csv_dir: str = "data/students", db_path: str = "data/students/university.db") -> Dict[str, int]:
    """Load data from CSV files into SQLite tables."""
    init_db(db_path)
    dir_path = Path(csv_dir)
    loaded_counts: Dict[str, int] = {}

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # 1. Load students.csv
        students_file = dir_path / "students.csv"
        if students_file.exists():
            with open(students_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        r["student_id"], r["full_name"], r["email"], r["programme"],
                        r["batch"], int(r["current_semester"]), float(r["cgpa"]),
                        r["standing"], r.get("holds", "")
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT OR REPLACE INTO students (
                    student_id, full_name, email, programme, batch,
                    current_semester, cgpa, standing, holds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            loaded_counts["students"] = len(rows)

        # 2. Load courses.csv
        courses_file = dir_path / "courses.csv"
        if courses_file.exists():
            with open(courses_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        r["course_code"], r["course_name"], r["programme"],
                        int(r["semester"]), int(r["credits"]), r["instructor"]
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT OR REPLACE INTO courses (
                    course_code, course_name, programme, semester, credits, instructor
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, rows)
            loaded_counts["courses"] = len(rows)

        # 3. Load attendance.csv
        attendance_file = dir_path / "attendance.csv"
        if attendance_file.exists():
            cursor.execute("DELETE FROM attendance;")  # Refresh table
            with open(attendance_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        r["student_id"], r["course_code"], int(r["classes_attended"]),
                        int(r["total_classes"]), float(r["attendance_percentage"])
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT INTO attendance (
                    student_id, course_code, classes_attended, total_classes, attendance_percentage
                ) VALUES (?, ?, ?, ?, ?)
            """, rows)
            loaded_counts["attendance"] = len(rows)

        # 4. Load results.csv
        results_file = dir_path / "results.csv"
        if results_file.exists():
            cursor.execute("DELETE FROM results;")  # Refresh table
            with open(results_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        r["student_id"], r["course_code"], int(r["semester"]),
                        r["grade"], float(r["grade_points"]), int(r["credits"]), r["status"]
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT INTO results (
                    student_id, course_code, semester, grade, grade_points, credits, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, rows)
            loaded_counts["results"] = len(rows)

        # 5. Load rule_registry.csv
        rules_file = dir_path / "rule_registry.csv"
        if rules_file.exists():
            with open(rules_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        r["rule_id"], r["rule_category"], r["description"],
                        r["parameter_name"], r["parameter_value"],
                        r["source_document"], r["clause"]
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT OR REPLACE INTO rule_registry (
                    rule_id, rule_category, description, parameter_name,
                    parameter_value, source_document, clause
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, rows)
            loaded_counts["rule_registry"] = len(rows)

        conn.commit()
    finally:
        conn.close()

    print(f"Successfully loaded CSV data into SQLite ({db_path}):")
    for tbl, count in loaded_counts.items():
        print(f"  - {tbl}: {count} records")
    return loaded_counts


if __name__ == "__main__":
    load_csv_data()
