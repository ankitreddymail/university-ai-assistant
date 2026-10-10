"""Student Data Access Tool (SQLite - Annex C Compliant).

Provides simple, readable helper functions to query:
- students
- courses
- attendance
- results
- rule_registry

from SQLite database strictly matching Annex C column names.
"""

import sqlite3
from typing import Optional, Dict, Any, List
from pathlib import Path


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Create a standard SQLite connection with row factory for dictionary access."""
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
            SELECT student_id, full_name, programme, batch_year,
                   current_semester, cgpa, active_backlogs, email, holds
            FROM students
            WHERE student_id = ?
            """,
            (student_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        data = dict(row)
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
    """Fetch attendance records for a student. Attendance percentage is calculated dynamically."""
    if not Path(db_path).exists():
        return []

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        if course_code:
            cursor.execute(
                """
                SELECT student_id, course_code, classes_held, classes_attended
                FROM attendance
                WHERE student_id = ? AND course_code = ?
                """,
                (student_id, course_code),
            )
        else:
            cursor.execute(
                """
                SELECT student_id, course_code, classes_held, classes_attended
                FROM attendance
                WHERE student_id = ?
                """,
                (student_id,),
            )
        records = []
        for row in cursor.fetchall():
            d = dict(row)
            held = d.get("classes_held", 0)
            attended = d.get("classes_attended", 0)
            # Calculated on demand, not stored as required field
            d["attendance_percentage"] = round((attended / held * 100), 1) if held > 0 else 0.0
            records.append(d)
        return records
    finally:
        conn.close()


def get_student_results(student_id: str, db_path: str) -> List[Dict[str, Any]]:
    """Fetch academic results for a student from results table."""
    if not Path(db_path).exists():
        return []

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT student_id, course_code, exam_session, exam_type,
                   internal_marks, external_marks, total_marks, max_marks, result
            FROM results
            WHERE student_id = ?
            """,
            (student_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_rules_by_parameter(parameter: str, db_path: str) -> List[Dict[str, Any]]:
    """Retrieve all business rules for a given parameter from rule_registry."""
    if not Path(db_path).exists():
        return []

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT rule_id, description, parameter, operator, value,
                   scope_programmes, scope_batches, effective_from,
                   effective_to, source_doc_id, source_section
            FROM rule_registry
            WHERE parameter = ?
            """,
            (parameter.strip(),),
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
            SELECT rule_id, description, parameter, operator, value,
                   scope_programmes, scope_batches, effective_from,
                   effective_to, source_doc_id, source_section
            FROM rule_registry
            WHERE rule_id = ?
            """,
            (rule_id.strip(),),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_rules(db_path: str) -> List[Dict[str, Any]]:
    """Retrieve all business rules from rule_registry."""
    if not Path(db_path).exists():
        return []

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT rule_id, description, parameter, operator, value,
                   scope_programmes, scope_batches, effective_from,
                   effective_to, source_doc_id, source_section
            FROM rule_registry
            ORDER BY rule_id ASC
            """
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
