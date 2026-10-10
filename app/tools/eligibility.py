"""Deterministic Student Eligibility Evaluation Tool.

Evaluates student records against academic and placement rules.
CRITICAL DESIGN RULES:
1. No hardcoded thresholds: all thresholds are retrieved dynamically from the rule_registry table.
2. Every determination must link to a documented source_document and clause.
3. If an applicable rule is not found in the registry, the system reports that it is unavailable
   rather than making assumptions.
"""

from typing import Dict, Any, List, Optional
from app.tools.student_data import (
    get_student_by_id,
    get_student_attendance,
    get_student_results,
    get_rules_by_category,
)


def check_attendance_eligibility(
    student_id: str,
    db_path: str,
    course_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Check if student meets the minimum attendance requirement to appear for exams.
    
    Dynamically fetches the attendance threshold from rule_registry.
    """
    # 1. Fetch attendance rules from registry first
    rules = get_rules_by_category("attendance", db_path)
    threshold_rule = next(
        (r for r in rules if r.get("parameter_name") == "min_attendance_percentage"),
        None,
    )

    if not threshold_rule:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": ["Applicable attendance rule is unavailable in the rule registry."],
            "rule_id": None,
            "source_document": None,
            "clause": None,
        }

    # 2. Check student record exists
    student = get_student_by_id(student_id, db_path)
    if not student:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": [f"Student record not found for ID: {student_id}"],
            "rule_id": threshold_rule["rule_id"],
            "source_document": threshold_rule["source_document"],
            "clause": threshold_rule["clause"],
        }

    min_pct = float(threshold_rule["parameter_value"])
    rule_id = threshold_rule["rule_id"]
    source_doc = threshold_rule["source_document"]
    clause = threshold_rule["clause"]

    attendance_records = get_student_attendance(student_id, db_path, course_code)
    if not attendance_records:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": [f"No attendance records found for student {student_id}" + (f" in course {course_code}" if course_code else "")],
            "rule_id": rule_id,
            "source_document": source_doc,
            "clause": clause,
        }

    reasons = []
    is_eligible = True

    for record in attendance_records:
        pct = float(record["attendance_percentage"])
        c_code = record["course_code"]
        if pct < min_pct:
            is_eligible = False
            reasons.append(
                f"Course {c_code}: Attendance {pct:.1f}% is below required {min_pct:.1f}% ({source_doc}, {clause})."
            )

    if is_eligible:
        reasons.append(
            f"Attendance satisfies the minimum requirement of {min_pct:.1f}% ({source_doc}, {clause})."
        )

    return {
        "student_id": student_id,
        "service_type": "attendance",
        "is_eligible": is_eligible,
        "reasons": reasons,
        "rule_id": rule_id,
        "source_document": source_doc,
        "clause": clause,
    }


def check_exam_result_eligibility(
    student_id: str,
    db_path: str,
) -> Dict[str, Any]:
    """Check student exam progression eligibility based on passing status and academic rules."""
    rules = get_rules_by_category("exam_result", db_path)
    if not rules:
        return {
            "student_id": student_id,
            "service_type": "exam_result",
            "is_eligible": False,
            "reasons": ["Applicable examination progression rule is unavailable in the rule registry."],
            "rule_id": None,
            "source_document": None,
            "clause": None,
        }

    student = get_student_by_id(student_id, db_path)
    if not student:
        return {
            "student_id": student_id,
            "service_type": "exam_result",
            "is_eligible": False,
            "reasons": [f"Student record not found for ID: {student_id}"],
            "rule_id": rules[0]["rule_id"],
            "source_document": rules[0]["source_document"],
            "clause": rules[0]["clause"],
        }

    primary_rule = rules[0]
    rule_id = primary_rule["rule_id"]
    source_doc = primary_rule["source_document"]
    clause = primary_rule["clause"]

    results = get_student_results(student_id, db_path)
    failed_courses = [r["course_code"] for r in results if r.get("status") in ("Fail", "Backlog")]

    reasons = []
    is_eligible = len(failed_courses) == 0

    if not is_eligible:
        reasons.append(f"Student has {len(failed_courses)} pending backlog(s): {', '.join(failed_courses)} ({source_doc}, {clause}).")
    else:
        reasons.append(f"Student has cleared all registered courses ({source_doc}, {clause}).")

    return {
        "student_id": student_id,
        "service_type": "exam_result",
        "is_eligible": is_eligible,
        "reasons": reasons,
        "rule_id": rule_id,
        "source_document": source_doc,
        "clause": clause,
    }


def check_supplementary_exam_eligibility(
    student_id: str,
    db_path: str,
    course_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Check eligibility to sit for supplementary/remedial examination."""
    rules = get_rules_by_category("supplementary_exam", db_path)
    backlog_limit_rule = next(
        (r for r in rules if r.get("parameter_name") == "max_backlogs_allowed"),
        None,
    )

    if not backlog_limit_rule:
        return {
            "student_id": student_id,
            "service_type": "supplementary_exam",
            "is_eligible": False,
            "reasons": ["Applicable supplementary exam rule is unavailable in the rule registry."],
            "rule_id": None,
            "source_document": None,
            "clause": None,
        }

    student = get_student_by_id(student_id, db_path)
    if not student:
        return {
            "student_id": student_id,
            "service_type": "supplementary_exam",
            "is_eligible": False,
            "reasons": [f"Student record not found for ID: {student_id}"],
            "rule_id": backlog_limit_rule["rule_id"],
            "source_document": backlog_limit_rule["source_document"],
            "clause": backlog_limit_rule["clause"],
        }

    max_backlogs = int(backlog_limit_rule["parameter_value"])
    rule_id = backlog_limit_rule["rule_id"]
    source_doc = backlog_limit_rule["source_document"]
    clause = backlog_limit_rule["clause"]

    results = get_student_results(student_id, db_path)
    failed_results = [r for r in results if r.get("status") in ("Fail", "Backlog", "Supplementary")]

    if not failed_results:
        return {
            "student_id": student_id,
            "service_type": "supplementary_exam",
            "is_eligible": False,
            "reasons": ["Student has no failed courses requiring supplementary examination."],
            "rule_id": rule_id,
            "source_document": source_doc,
            "clause": clause,
        }

    reasons = []
    if len(failed_results) > max_backlogs:
        is_eligible = False
        reasons.append(
            f"Active backlogs ({len(failed_results)}) exceed maximum allowed limit of {max_backlogs} for supplementary exams ({source_doc}, {clause})."
        )
    else:
        is_eligible = True
        failed_codes = [r["course_code"] for r in failed_results]
        reasons.append(
            f"Eligible for supplementary exams in: {', '.join(failed_codes)} ({source_doc}, {clause})."
        )

    return {
        "student_id": student_id,
        "service_type": "supplementary_exam",
        "is_eligible": is_eligible,
        "reasons": reasons,
        "rule_id": rule_id,
        "source_document": source_doc,
        "clause": clause,
    }


def check_placement_eligibility(
    student_id: str,
    db_path: str,
) -> Dict[str, Any]:
    """Check campus placement drive eligibility using documented placement rules."""
    rules = get_rules_by_category("placement", db_path)
    min_cgpa_rule = next(
        (r for r in rules if r.get("parameter_name") == "min_cgpa"),
        None,
    )
    backlog_rule = next(
        (r for r in rules if r.get("parameter_name") == "max_active_backlogs"),
        None,
    )

    if not min_cgpa_rule or not backlog_rule:
        return {
            "student_id": student_id,
            "service_type": "placement",
            "is_eligible": False,
            "reasons": ["Applicable placement criteria rules are unavailable in the rule registry."],
            "rule_id": None,
            "source_document": None,
            "clause": None,
        }

    student = get_student_by_id(student_id, db_path)
    if not student:
        return {
            "student_id": student_id,
            "service_type": "placement",
            "is_eligible": False,
            "reasons": [f"Student record not found for ID: {student_id}"],
            "rule_id": min_cgpa_rule["rule_id"],
            "source_document": min_cgpa_rule["source_document"],
            "clause": f"{min_cgpa_rule['clause']}, {backlog_rule['clause']}",
        }

    min_cgpa = float(min_cgpa_rule["parameter_value"])
    max_backlogs = int(backlog_rule["parameter_value"])
    rule_id = min_cgpa_rule["rule_id"]
    source_doc = min_cgpa_rule["source_document"]
    clause = f"{min_cgpa_rule['clause']}, {backlog_rule['clause']}"

    student_cgpa = float(student.get("cgpa", 0.0))
    results = get_student_results(student_id, db_path)
    active_backlogs = [r for r in results if r.get("status") in ("Fail", "Backlog")]
    holds = student.get("holds", [])

    reasons = []
    is_eligible = True

    if student_cgpa < min_cgpa:
        is_eligible = False
        reasons.append(
            f"CGPA {student_cgpa:.2f} is below the required {min_cgpa:.2f} threshold ({min_cgpa_rule['source_document']}, {min_cgpa_rule['clause']})."
        )

    if len(active_backlogs) > max_backlogs:
        is_eligible = False
        reasons.append(
            f"Student has {len(active_backlogs)} active backlogs (max allowed: {max_backlogs}) ({backlog_rule['source_document']}, {backlog_rule['clause']})."
        )

    if holds:
        is_eligible = False
        reasons.append(f"Active holds detected: {', '.join(holds)}.")

    if is_eligible:
        reasons.append(
            f"Student meets placement eligibility criteria (CGPA >= {min_cgpa:.2f}, backlogs <= {max_backlogs}) ({source_doc}, {clause})."
        )

    return {
        "student_id": student_id,
        "service_type": "placement",
        "is_eligible": is_eligible,
        "reasons": reasons,
        "rule_id": rule_id,
        "source_document": source_doc,
        "clause": clause,
    }
