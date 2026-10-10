"""Script to initialize SQLite database and load student records from CSV (Annex C).

Creates the 5 SQLite tables:
1. students: student_id, full_name, programme, batch_year, current_semester, cgpa, active_backlogs, (optional: email, holds)
2. courses: course_code, course_name, programme, semester, credits
3. attendance: student_id, course_code, classes_held, classes_attended
4. results: student_id, course_code, exam_session, exam_type, internal_marks, external_marks, total_marks, max_marks, result
5. rule_registry: rule_id, description, parameter, operator, value, scope_programmes, scope_batches, effective_from, effective_to, source_doc_id, source_section
"""

import csv
import sqlite3
from pathlib import Path
from typing import Dict, Any


def init_db(db_path: str) -> None:
    """Drop and recreate all 5 tables strictly conforming to Annex C."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()

        # Drop old tables to ensure schema compliance
        cursor.execute("DROP TABLE IF EXISTS attendance;")
        cursor.execute("DROP TABLE IF EXISTS results;")
        cursor.execute("DROP TABLE IF EXISTS courses;")
        cursor.execute("DROP TABLE IF EXISTS students;")
        cursor.execute("DROP TABLE IF EXISTS rule_registry;")

        # 1. students
        cursor.execute("""
            CREATE TABLE students (
                student_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                programme TEXT NOT NULL,
                batch_year INTEGER NOT NULL,
                current_semester INTEGER NOT NULL,
                cgpa REAL NOT NULL,
                active_backlogs INTEGER NOT NULL,
                email TEXT,
                holds TEXT DEFAULT ''
            );
        """)

        # 2. courses
        cursor.execute("""
            CREATE TABLE courses (
                course_code TEXT PRIMARY KEY,
                course_name TEXT NOT NULL,
                programme TEXT NOT NULL,
                semester INTEGER NOT NULL,
                credits INTEGER NOT NULL
            );
        """)

        # 3. attendance (percentage is calculated, not stored as required field)
        cursor.execute("""
            CREATE TABLE attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_code TEXT NOT NULL,
                classes_held INTEGER NOT NULL,
                classes_attended INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_code) REFERENCES courses(course_code)
            );
        """)

        # 4. results
        cursor.execute("""
            CREATE TABLE results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_code TEXT NOT NULL,
                exam_session TEXT NOT NULL,
                exam_type TEXT NOT NULL,
                internal_marks REAL NOT NULL,
                external_marks REAL NOT NULL,
                total_marks REAL NOT NULL,
                max_marks REAL NOT NULL,
                result TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (course_code) REFERENCES courses(course_code)
            );
        """)

        # 5. rule_registry
        cursor.execute("""
            CREATE TABLE rule_registry (
                rule_id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                parameter TEXT NOT NULL,
                operator TEXT NOT NULL,
                value TEXT NOT NULL,
                scope_programmes TEXT NOT NULL,
                scope_batches TEXT NOT NULL,
                effective_from TEXT NOT NULL,
                effective_to TEXT NOT NULL,
                source_doc_id TEXT NOT NULL,
                source_section TEXT NOT NULL
            );
        """)

        conn.commit()
    finally:
        conn.close()


def load_csv_data(csv_dir: str = "data/students", db_path: str = "data/students/university.db") -> Dict[str, int]:
    """Load data from CSV files into SQLite tables conforming to Annex C."""
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
                        r["student_id"], r["full_name"], r["programme"],
                        int(r["batch_year"]), int(r["current_semester"]),
                        float(r["cgpa"]), int(r["active_backlogs"]),
                        r.get("email", ""), r.get("holds", "")
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT OR REPLACE INTO students (
                    student_id, full_name, programme, batch_year,
                    current_semester, cgpa, active_backlogs, email, holds
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
                        int(r["semester"]), int(r["credits"])
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT OR REPLACE INTO courses (
                    course_code, course_name, programme, semester, credits
                ) VALUES (?, ?, ?, ?, ?)
            """, rows)
            loaded_counts["courses"] = len(rows)

        # 3. Load attendance.csv
        attendance_file = dir_path / "attendance.csv"
        if attendance_file.exists():
            with open(attendance_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        r["student_id"], r["course_code"],
                        int(r["classes_held"]), int(r["classes_attended"])
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT INTO attendance (
                    student_id, course_code, classes_held, classes_attended
                ) VALUES (?, ?, ?, ?)
            """, rows)
            loaded_counts["attendance"] = len(rows)

        # 4. Load results.csv
        results_file = dir_path / "results.csv"
        if results_file.exists():
            with open(results_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        r["student_id"], r["course_code"], r["exam_session"],
                        r["exam_type"], float(r["internal_marks"]),
                        float(r["external_marks"]), float(r["total_marks"]),
                        float(r["max_marks"]), r["result"]
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT INTO results (
                    student_id, course_code, exam_session, exam_type,
                    internal_marks, external_marks, total_marks, max_marks, result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            loaded_counts["results"] = len(rows)

        # 5. Load rule_registry.csv
        rules_file = dir_path / "rule_registry.csv"
        if rules_file.exists():
            with open(rules_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = [
                    (
                        r["rule_id"], r["description"], r["parameter"],
                        r["operator"], r["value"], r["scope_programmes"],
                        r["scope_batches"], r["effective_from"],
                        r["effective_to"], r["source_doc_id"], r["source_section"]
                    )
                    for r in reader
                ]
            cursor.executemany("""
                INSERT OR REPLACE INTO rule_registry (
                    rule_id, description, parameter, operator, value,
                    scope_programmes, scope_batches, effective_from,
                    effective_to, source_doc_id, source_section
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            loaded_counts["rule_registry"] = len(rows)

        conn.commit()
    finally:
        conn.close()

    print(f"Loaded Annex C CSV data into SQLite ({db_path}):")
    for tbl, count in loaded_counts.items():
        print(f"  - {tbl}: {count} records")
    return loaded_counts


if __name__ == "__main__":
    load_csv_data()
