"""Script to initialize SQLite database and load student records.

Creates the 'students' table schema and inserts records from students.json.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any


def init_db(db_path: str) -> None:
    """Create students table schema if it does not already exist."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                major TEXT NOT NULL,
                gpa REAL NOT NULL,
                credits_completed INTEGER NOT NULL,
                standing TEXT NOT NULL,
                holds TEXT DEFAULT ''
            );
        """)
        conn.commit()
    finally:
        conn.close()


def load_students_to_sqlite(json_path: str, db_path: str) -> int:
    """Insert or replace student records from JSON file into SQLite database."""
    init_db(db_path)

    json_file = Path(json_path)
    if not json_file.exists():
        print(f"Error: {json_path} does not exist.")
        return 0

    with open(json_file, "r", encoding="utf-8") as f:
        records: List[Dict[str, Any]] = json.load(f)

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        for r in records:
            holds_str = ",".join(r.get("holds", []))
            cursor.execute("""
                INSERT OR REPLACE INTO students (
                    student_id, full_name, email, major, gpa, credits_completed, standing, holds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r["student_id"],
                r["full_name"],
                r["email"],
                r["major"],
                float(r["gpa"]),
                int(r["credits_completed"]),
                r["standing"],
                holds_str
            ))
        conn.commit()
        print(f"Successfully loaded {len(records)} students into SQLite ({db_path}).")
        return len(records)
    finally:
        conn.close()


if __name__ == "__main__":
    load_students_to_sqlite("data/students/students.json", "data/students/university.db")
