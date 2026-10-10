"""Tests for deterministic eligibility checks and rule registry lookups."""

import sqlite3
import pytest
from app.tools.eligibility import (
    check_attendance_eligibility,
    check_placement_eligibility,
    check_supplementary_exam_eligibility,
)
from scripts.load_students import init_db, load_csv_data


@pytest.fixture(scope="module")
def test_db_path(tmp_path_factory):
    """Create a temporary test database populated from CSVs."""
    db_file = tmp_path_factory.mktemp("data") / "test_university.db"
    load_csv_data(csv_dir="data/students", db_path=str(db_file))
    return str(db_file)


def test_attendance_eligibility_with_rule(test_db_path):
    """Verify attendance check uses rule from registry and identifies pass/shortage."""
    # S1001 has high attendance (> 75%)
    res = check_attendance_eligibility(student_id="S1001", db_path=test_db_path)
    assert res["is_eligible"] is True
    assert res["rule_id"] == "ATT_MIN_01"
    assert "academic_regulations_2024.pdf" in res["source_document"]


def test_missing_rule_reports_unavailable(tmp_path):
    """Verify system reports unavailable if rule is not in registry."""
    empty_db = tmp_path / "empty.db"
    init_db(str(empty_db))
    # No rules loaded
    res = check_attendance_eligibility(student_id="S1001", db_path=str(empty_db))
    assert res["is_eligible"] is False
    assert any("unavailable" in r.lower() for r in res["reasons"])


def test_placement_eligibility_with_rules(test_db_path):
    """Verify placement eligibility checks CGPA and backlogs against rule registry."""
    res = check_placement_eligibility(student_id="S1001", db_path=test_db_path)
    # S1001 has high CGPA and 0 backlogs
    assert res["is_eligible"] is True
    assert res["rule_id"] == "PLACE_CGPA_01"
    assert "placement_policy_2024.pdf" in res["source_document"]
