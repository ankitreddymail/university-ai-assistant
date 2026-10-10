"""Student Data Access Tool (SQLite).

Provides simple functions to query student profile, academic standing,
completed credits, and active holds from a local SQLite database.
"""

import sqlite3
from typing import Optional, Dict, Any
from pathlib import Path


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Create a standard SQLite connection with row factory for dictionary access."""
    # Ensure parent directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_student_by_id(student_id: str, db_path: str) -> Optional[Dict[str, Any]]:
    """Fetch a student's basic record by their unique student ID.
    
    Returns a dict with student attributes or None if not found.
    """
    if not Path(db_path).exists():
        return None

    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT student_id, full_name, email, major, gpa, credits_completed, standing, holds FROM students WHERE student_id = ?",
            (student_id,)
        )
        row = cursor.fetchone()
        if row:
            data = dict(row)
            # Holds are stored as comma-separated text; convert to list
            holds_raw = data.get("holds") or ""
            data["holds"] = [h.strip() for h in holds_raw.split(",") if h.strip()]
            return data
        return None
    finally:
        conn.close()
