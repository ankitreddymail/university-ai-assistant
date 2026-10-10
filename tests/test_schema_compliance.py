"""Programmatic verification of SQLite schema against Annex C specifications."""

import sqlite3
import pytest
from pathlib import Path
from scripts.load_students import load_csv_data

ANNEX_C_REQUIRED_COLUMNS = {
    "students": {
        "student_id", "full_name", "programme", "batch_year",
        "current_semester", "cgpa", "active_backlogs"
    },
    "courses": {
        "course_code", "course_name", "programme", "semester", "credits"
    },
    "attendance": {
        "student_id", "course_code", "classes_held", "classes_attended"
    },
    "results": {
        "student_id", "course_code", "exam_session", "exam_type",
        "internal_marks", "external_marks", "total_marks", "max_marks", "result"
    },
    "rule_registry": {
        "rule_id", "description", "parameter", "operator", "value",
        "scope_programmes", "scope_batches", "effective_from", "effective_to",
        "source_doc_id", "source_section"
    },
}


@pytest.fixture(scope="module")
def db_conn():
    """Ensure database is loaded and return SQLite connection."""
    db_path = "data/students/university.db"
    load_csv_data(csv_dir="data/students", db_path=db_path)
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


def test_all_five_tables_exist(db_conn):
    """Verify that all five required tables exist in the database."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = {row[0] for row in cursor.fetchall()}
    for req_table in ANNEX_C_REQUIRED_COLUMNS:
        assert req_table in tables, f"Missing required table: {req_table}"


@pytest.mark.parametrize("table_name, required_cols", ANNEX_C_REQUIRED_COLUMNS.items())
def test_table_columns_comply_with_annex_c(db_conn, table_name, required_cols):
    """Verify each table contains every required column name exactly."""
    cursor = db_conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    actual_cols = {col[1] for col in cursor.fetchall()}

    missing = required_cols - actual_cols
    assert not missing, f"Table '{table_name}' is missing required Annex C column(s): {missing}"


def test_judge_reservations(db_conn):
    """Verify judge ID range S9000-S9999 and course prefix JDG are not used."""
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students WHERE student_id LIKE 'S9%';")
    assert cursor.fetchone()[0] == 0, "Student IDs in S9000-S9999 must be reserved for judges."

    cursor.execute("SELECT COUNT(*) FROM courses WHERE course_code LIKE 'JDG%';")
    assert cursor.fetchone()[0] == 0, "Course codes beginning with JDG must be reserved for judges."
