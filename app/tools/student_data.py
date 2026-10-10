"""Student Data Access Tool (SQLite).

Provides simple, readable helper functions to query:
- students
- courses
- attendance
- results
- rule_registry

from the local SQLite database according to the Annex C schema.
"""

import sqlite3
from typing import Optional, Dict, Any, List
from pathlib import Path


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Create a standard SQLite connection with row factory for dictionary-like access."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_student_by_id(student_id: str, db_path: str) -> Optional[Dict[str, Any]]:
    """Fetch a student's record by student_id from the students table."""
    if not Path(db_path).exists():
        return None

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT student_id, full_name, email, programme, batch,
                   current_semester, cgpa, standing, holds
            FROM students
            WHERE student_id = ?
            """,
            (student_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        data = dict(row)
        # Parse comma-separated holds into a list of strings
        raw_holds = data.get("holds") or ""
        data["holds"] = [h.strip() for h in raw_holds.split(",") if h.strip()]
        return data
    finally:
        conn.close()


def get_student_attendance(
    student_id: str,
    db_path: str,
    course_code: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetch attendance records for a student, optionally filtered by course_code."""
    if not Path(db_path).exists():
        return []

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        if course_code:
            cursor.execute(
                """
                SELECT student_id, course_code, classes_attended, total_classes, attendance_percentage
                FROM attendance
                WHERE student_id = ? AND course_code = ?
                """,
                (student_id, course_code),
            )
        else:
            cursor.execute(
                """
                SELECT student_id, course_code, classes_attended, total_classes, attendance_percentage
                FROM attendance
                WHERE student_id = ?
                """,
                (student_id,),
            )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_student_results(student_id: str, db_path: str) -> List[Dict[str, Any]]:
    """Fetch academic results and grades for a student."""
    if not Path(db_path).exists():
        return []

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT student_id, course_code, semester, grade, grade_points, credits, status
            FROM results
            WHERE student_id = ?
            ORDER BY semester ASC
            """,
            (student_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_rules_by_category(category: str, db_path: str) -> List[Dict[str, Any]]:
    """Retrieve all business rules belonging to a category from rule_registry."""
    if not Path(db_path).exists():
        return []

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT rule_id, rule_category, description, parameter_name,
                   parameter_value, source_document, clause
            FROM rule_registry
            WHERE rule_category = ?
            """,
            (category.strip().lower(),),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_rule_by_id(rule_id: str, db_path: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single rule by its unique rule_id from rule_registry."""
    if not Path(db_path).exists():
        return None

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT rule_id, rule_category, description, parameter_name,
                   parameter_value, source_document, clause
            FROM rule_registry
            WHERE rule_id = ?
            """,
            (rule_id.strip(),),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
