"""Deterministic Student Eligibility Evaluation Tool (Annex C Compliant).

Evaluates student records against rules stored in rule_registry.
All thresholds come from rule_registry and cite source_doc_id and source_section.
"""

from typing import Dict, Any, List, Optional
from app.tools.student_data import (
    get_student_by_id,
    get_student_attendance,
    get_student_results,
    get_rules_by_parameter,
)


def check_attendance_eligibility(
    student_id: str,
    db_path: str,
    course_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Check if student meets the minimum attendance requirement to appear for exams."""
    # 1. Fetch attendance rules from registry first
    rules = get_rules_by_parameter("min_attendance_percentage", db_path)
    if not rules:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": ["Applicable attendance rule is unavailable in the rule registry."],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    threshold_rule = rules[0]
    min_pct = float(threshold_rule["value"])
    rule_id = threshold_rule["rule_id"]
    source_doc_id = threshold_rule["source_doc_id"]
    source_section = threshold_rule["source_section"]

    # 2. Check student record exists
    student = get_student_by_id(student_id, db_path)
    if not student:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": [f"Student record not found for ID: {student_id}"],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    attendance_records = get_student_attendance(student_id, db_path, course_code)
    if not attendance_records:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": [f"No attendance records found for student {student_id}" + (f" in course {course_code}" if course_code else "")],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    reasons = []
    is_eligible = True

    for record in attendance_records:
        pct = float(record["attendance_percentage"])
        c_code = record["course_code"]
        held = record["classes_held"]
        attended = record["classes_attended"]
        if pct < min_pct:
            is_eligible = False
            reasons.append(
                f"Course {c_code}: Attended {attended}/{held} classes ({pct:.1f}%), below required {min_pct:.1f}% ({source_doc_id}, {source_section})."
            )

    if is_eligible:
        reasons.append(
            f"Attendance satisfies the minimum requirement of {min_pct:.1f}% ({source_doc_id}, {source_section})."
        )

    return {
        "student_id": student_id,
        "service_type": "attendance",
        "is_eligible": is_eligible,
        "reasons": reasons,
        "rule_id": rule_id,
        "source_doc_id": source_doc_id,
        "source_section": source_section,
    }


def check_exam_result_eligibility(
    student_id: str,
    db_path: str,
) -> Dict[str, Any]:
    """Check student exam progression eligibility based on passing status and academic rules."""
    rules = get_rules_by_parameter("min_total_marks", db_path)
    if not rules:
        return {
            "student_id": student_id,
            "service_type": "exam_result",
            "is_eligible": False,
            "reasons": ["Applicable examination progression rule is unavailable in the rule registry."],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    threshold_rule = rules[0]
    rule_id = threshold_rule["rule_id"]
    source_doc_id = threshold_rule["source_doc_id"]
    source_section = threshold_rule["source_section"]

    student = get_student_by_id(student_id, db_path)
    if not student:
        return {
            "student_id": student_id,
            "service_type": "exam_result",
            "is_eligible": False,
            "reasons": [f"Student record not found for ID: {student_id}"],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    results = get_student_results(student_id, db_path)
    failed_courses = [r["course_code"] for r in results if r.get("result") == "Fail"]

    reasons = []
    is_eligible = len(failed_courses) == 0

    if not is_eligible:
        reasons.append(f"Student has {len(failed_courses)} pending backlog(s): {', '.join(failed_courses)} ({source_doc_id}, {source_section}).")
    else:
        reasons.append(f"Student has passed all completed examinations ({source_doc_id}, {source_section}).")

    return {
        "student_id": student_id,
        "service_type": "exam_result",
        "is_eligible": is_eligible,
        "reasons": reasons,
        "rule_id": rule_id,
        "source_doc_id": source_doc_id,
        "source_section": source_section,
    }


def check_supplementary_exam_eligibility(
    student_id: str,
    db_path: str,
    course_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Check eligibility to register for supplementary examinations."""
    rules = get_rules_by_parameter("max_backlogs_allowed", db_path)
    if not rules:
        return {
            "student_id": student_id,
            "service_type": "supplementary_exam",
            "is_eligible": False,
            "reasons": ["Applicable supplementary exam rule is unavailable in the rule registry."],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    backlog_limit_rule = rules[0]
    max_backlogs = int(backlog_limit_rule["value"])
    rule_id = backlog_limit_rule["rule_id"]
    source_doc_id = backlog_limit_rule["source_doc_id"]
    source_section = backlog_limit_rule["source_section"]

    student = get_student_by_id(student_id, db_path)
    if not student:
        return {
            "student_id": student_id,
            "service_type": "supplementary_exam",
            "is_eligible": False,
            "reasons": [f"Student record not found for ID: {student_id}"],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    results = get_student_results(student_id, db_path)
    failed_results = [r for r in results if r.get("result") == "Fail"]

    if not failed_results:
        return {
            "student_id": student_id,
            "service_type": "supplementary_exam",
            "is_eligible": False,
            "reasons": ["Student has no failed courses requiring supplementary examination."],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    reasons = []
    if len(failed_results) > max_backlogs:
        is_eligible = False
        reasons.append(
            f"Active backlogs ({len(failed_results)}) exceed maximum allowed limit of {max_backlogs} for supplementary exams ({source_doc_id}, {source_section})."
        )
    else:
        is_eligible = True
        failed_codes = [r["course_code"] for r in failed_results]
        reasons.append(
            f"Eligible for supplementary exams in: {', '.join(failed_codes)} ({source_doc_id}, {source_section})."
        )

    return {
        "student_id": student_id,
        "service_type": "supplementary_exam",
        "is_eligible": is_eligible,
        "reasons": reasons,
        "rule_id": rule_id,
        "source_doc_id": source_doc_id,
        "source_section": source_section,
    }


def check_placement_eligibility(
    student_id: str,
    db_path: str,
) -> Dict[str, Any]:
    """Check campus placement drive eligibility using documented placement rules."""
    cgpa_rules = get_rules_by_parameter("min_cgpa", db_path)
    backlog_rules = get_rules_by_parameter("max_active_backlogs", db_path)

    if not cgpa_rules or not backlog_rules:
        return {
            "student_id": student_id,
            "service_type": "placement",
            "is_eligible": False,
            "reasons": ["Applicable placement criteria rules are unavailable in the rule registry."],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    min_cgpa_rule = cgpa_rules[0]
    backlog_rule = backlog_rules[0]

    min_cgpa = float(min_cgpa_rule["value"])
    max_backlogs = int(backlog_rule["value"])
    rule_id = min_cgpa_rule["rule_id"]
    source_doc_id = min_cgpa_rule["source_doc_id"]
    source_section = f"{min_cgpa_rule['source_section']}, {backlog_rule['source_section']}"

    student = get_student_by_id(student_id, db_path)
    if not student:
        return {
            "student_id": student_id,
            "service_type": "placement",
            "is_eligible": False,
            "reasons": [f"Student record not found for ID: {student_id}"],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    student_cgpa = float(student.get("cgpa", 0.0))
    active_backlogs = int(student.get("active_backlogs", 0))
    holds = student.get("holds", [])

    reasons = []
    is_eligible = True

    if student_cgpa < min_cgpa:
        is_eligible = False
        reasons.append(
            f"CGPA {student_cgpa:.2f} is below the required {min_cgpa:.2f} threshold ({min_cgpa_rule['source_doc_id']}, {min_cgpa_rule['source_section']})."
        )

    if active_backlogs > max_backlogs:
        is_eligible = False
        reasons.append(
            f"Student has {active_backlogs} active backlog(s) (max allowed: {max_backlogs}) ({backlog_rule['source_doc_id']}, {backlog_rule['source_section']})."
        )

    if holds:
        is_eligible = False
        reasons.append(f"Active holds detected: {', '.join(holds)}.")

    if is_eligible:
        reasons.append(
            f"Student meets placement eligibility criteria (CGPA >= {min_cgpa:.2f}, active backlogs <= {max_backlogs}) ({source_doc_id}, {source_section})."
        )

    return {
        "student_id": student_id,
        "service_type": "placement",
        "is_eligible": is_eligible,
        "reasons": reasons,
        "rule_id": rule_id,
        "source_doc_id": source_doc_id,
        "source_section": source_section,
    }
