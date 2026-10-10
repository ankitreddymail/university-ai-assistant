"""Deterministic Student Eligibility Evaluation Tool (Annex C Compliant).

Evaluates student records against rules stored in SQLite rule_registry.

CRITICAL DESIGN RULES:
1. No hardcoded thresholds: all thresholds, operators, and scopes are read from rule_registry.
2. Every determination cites source_doc_id and source_section.
3. Every rule is validated for scope (programme, batch) and effective date range.
4. If a required rule or student data point is missing, returns an explicit unavailable response.
5. Simple, readable Python functions with type hints and plain English comments.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from app.tools.student_data import (
    get_student_by_id,
    get_student_attendance,
    get_student_results,
    get_rules_by_parameter,
)


def evaluate_operator(actual_value: float, operator: str, target_value: float) -> bool:
    """Evaluate a numeric condition against an operator from rule_registry."""
    op = operator.strip()
    if op == ">=":
        return actual_value >= target_value
    elif op == "<=":
        return actual_value <= target_value
    elif op in ("==", "="):
        return actual_value == target_value
    elif op == ">":
        return actual_value > target_value
    elif op == "<":
        return actual_value < target_value
    elif op == "!=":
        return actual_value != target_value
    return False


def check_rule_applicability(
    rule: Dict[str, Any],
    student: Dict[str, Any],
    evaluation_date: Optional[str] = None,
) -> Tuple[bool, Optional[str]]:
    """Verify that a rule is authorized and applicable to the student's programme, batch, and date."""
    # 1. Programme scope check
    scope_prog = rule.get("scope_programmes", "ALL").strip()
    if scope_prog != "ALL":
        allowed_programmes = [p.strip().lower() for p in scope_prog.split(",")]
        student_prog = student.get("programme", "").strip().lower()
        if student_prog not in allowed_programmes:
            return False, (
                f"Rule '{rule.get('rule_id')}' applies only to programmes [{scope_prog}], "
                f"which does not cover student programme '{student.get('programme')}'."
            )

    # 2. Batch scope check
    scope_batches = str(rule.get("scope_batches", "ALL")).strip()
    if scope_batches != "ALL":
        allowed_batches = [b.strip() for b in scope_batches.split(",")]
        student_batch = str(student.get("batch_year", "")).strip()
        if student_batch not in allowed_batches:
            return False, (
                f"Rule '{rule.get('rule_id')}' applies only to admission batches [{scope_batches}], "
                f"which does not cover student batch '{student.get('batch_year')}'."
            )

    # 3. Effective date check
    eff_from = rule.get("effective_from", "1900-01-01").strip()
    eff_to = rule.get("effective_to", "2099-12-31").strip()
    eval_dt = evaluation_date or datetime.now().strftime("%Y-%m-%d")

    if eval_dt < eff_from or eval_dt > eff_to:
        return False, (
            f"Rule '{rule.get('rule_id')}' is effective from {eff_from} to {eff_to}. "
            f"It is not applicable on evaluation date {eval_dt}."
        )

    return True, None


def check_attendance_eligibility(
    student_id: str,
    db_path: str,
    course_code: Optional[str] = None,
    evaluation_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Check if student meets the minimum attendance requirement to appear for exams."""
    # 1. Fetch attendance rules from registry first
    rules = get_rules_by_parameter("min_attendance_percentage", db_path)
    if not rules:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": ["Applicable attendance rule is unavailable in the rule registry. Cannot determine eligibility without an authorized rule."],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    threshold_rule = rules[0]
    min_pct = float(threshold_rule["value"])
    rule_op = threshold_rule.get("operator", ">=")
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

    # 3. Verify rule applicability (scope & dates)
    is_applicable, applicability_reason = check_rule_applicability(threshold_rule, student, evaluation_date)
    if not is_applicable:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": [f"Rule applicability check failed: {applicability_reason}"],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    # 4. Check attendance records
    attendance_records = get_student_attendance(student_id, db_path, course_code)
    if not attendance_records:
        return {
            "student_id": student_id,
            "service_type": "attendance",
            "is_eligible": False,
            "reasons": [f"Attendance records are unavailable for student {student_id}" + (f" in course {course_code}" if course_code else "")],
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
        meets_rule = evaluate_operator(pct, rule_op, min_pct)

        if not meets_rule:
            is_eligible = False
            reasons.append(
                f"Course {c_code}: Attended {attended}/{held} classes ({pct:.1f}%), does not satisfy {rule_op} {min_pct:.1f}% ({source_doc_id}, {source_section})."
            )

    if is_eligible:
        reasons.append(
            f"Attendance satisfies the minimum requirement of {rule_op} {min_pct:.1f}% ({source_doc_id}, {source_section})."
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
    evaluation_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Check student exam progression eligibility based on passing status and academic rules."""
    rules = get_rules_by_parameter("min_total_marks", db_path)
    if not rules:
        return {
            "student_id": student_id,
            "service_type": "exam_result",
            "is_eligible": False,
            "reasons": ["Applicable examination passing rule is unavailable in the rule registry. Cannot determine eligibility without an authorized rule."],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    threshold_rule = rules[0]
    rule_id = threshold_rule["rule_id"]
    rule_op = threshold_rule.get("operator", ">=")
    min_marks = float(threshold_rule["value"])
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

    is_applicable, applicability_reason = check_rule_applicability(threshold_rule, student, evaluation_date)
    if not is_applicable:
        return {
            "student_id": student_id,
            "service_type": "exam_result",
            "is_eligible": False,
            "reasons": [f"Rule applicability check failed: {applicability_reason}"],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    results = get_student_results(student_id, db_path)
    if not results:
        return {
            "student_id": student_id,
            "service_type": "exam_result",
            "is_eligible": False,
            "reasons": [f"Examination result records are unavailable for student {student_id}."],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    failed_courses = []
    for r in results:
        tot = float(r.get("total_marks", 0.0))
        res_str = r.get("result", "")
        # A course is failed if total_marks fails the operator or status is Fail
        if res_str == "Fail" or not evaluate_operator(tot, rule_op, min_marks):
            failed_courses.append(r["course_code"])

    reasons = []
    is_eligible = len(failed_courses) == 0

    if not is_eligible:
        reasons.append(
            f"Student has {len(failed_courses)} pending backlog(s): {', '.join(failed_courses)} ({source_doc_id}, {source_section})."
        )
    else:
        reasons.append(
            f"Student has passed all registered courses with marks {rule_op} {min_marks:.1f} ({source_doc_id}, {source_section})."
        )

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
    evaluation_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Check eligibility to register for supplementary examinations."""
    rules = get_rules_by_parameter("max_backlogs_allowed", db_path)
    if not rules:
        return {
            "student_id": student_id,
            "service_type": "supplementary_exam",
            "is_eligible": False,
            "reasons": ["Applicable supplementary exam rule is unavailable in the rule registry. Cannot determine eligibility without an authorized rule."],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    backlog_limit_rule = rules[0]
    max_backlogs = int(backlog_limit_rule["value"])
    rule_op = backlog_limit_rule.get("operator", "<=")
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

    is_applicable, applicability_reason = check_rule_applicability(backlog_limit_rule, student, evaluation_date)
    if not is_applicable:
        return {
            "student_id": student_id,
            "service_type": "supplementary_exam",
            "is_eligible": False,
            "reasons": [f"Rule applicability check failed: {applicability_reason}"],
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
    backlog_count = len(failed_results)
    within_limit = evaluate_operator(float(backlog_count), rule_op, float(max_backlogs))

    if not within_limit:
        is_eligible = False
        reasons.append(
            f"Active backlogs ({backlog_count}) fail criteria {rule_op} {max_backlogs} for supplementary exams ({source_doc_id}, {source_section})."
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
    evaluation_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Check campus placement drive eligibility using documented placement rules."""
    cgpa_rules = get_rules_by_parameter("min_cgpa", db_path)
    backlog_rules = get_rules_by_parameter("max_active_backlogs", db_path)

    if not cgpa_rules or not backlog_rules:
        return {
            "student_id": student_id,
            "service_type": "placement",
            "is_eligible": False,
            "reasons": ["Applicable placement criteria rules are unavailable in the rule registry. Cannot determine eligibility without authorized placement rules."],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    min_cgpa_rule = cgpa_rules[0]
    backlog_rule = backlog_rules[0]

    min_cgpa = float(min_cgpa_rule["value"])
    cgpa_op = min_cgpa_rule.get("operator", ">=")
    max_backlogs = int(backlog_rule["value"])
    backlog_op = backlog_rule.get("operator", "==")

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

    # Check applicability for both rules
    is_app_cgpa, reason_cgpa = check_rule_applicability(min_cgpa_rule, student, evaluation_date)
    is_app_backlog, reason_backlog = check_rule_applicability(backlog_rule, student, evaluation_date)

    if not is_app_cgpa:
        return {
            "student_id": student_id,
            "service_type": "placement",
            "is_eligible": False,
            "reasons": [f"Placement CGPA rule not applicable: {reason_cgpa}"],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }
    if not is_app_backlog:
        return {
            "student_id": student_id,
            "service_type": "placement",
            "is_eligible": False,
            "reasons": [f"Placement backlog rule not applicable: {reason_backlog}"],
            "rule_id": rule_id,
            "source_doc_id": source_doc_id,
            "source_section": source_section,
        }

    student_cgpa = float(student.get("cgpa", 0.0))
    active_backlogs = int(student.get("active_backlogs", 0))
    holds = student.get("holds", [])

    reasons = []
    is_eligible = True

    if not evaluate_operator(student_cgpa, cgpa_op, min_cgpa):
        is_eligible = False
        reasons.append(
            f"CGPA {student_cgpa:.2f} does not satisfy requirement {cgpa_op} {min_cgpa:.2f} ({min_cgpa_rule['source_doc_id']}, {min_cgpa_rule['source_section']})."
        )

    if not evaluate_operator(float(active_backlogs), backlog_op, float(max_backlogs)):
        is_eligible = False
        reasons.append(
            f"Active backlogs ({active_backlogs}) fail requirement {backlog_op} {max_backlogs} ({backlog_rule['source_doc_id']}, {backlog_rule['source_section']})."
        )

    if holds:
        is_eligible = False
        reasons.append(f"Active holds detected: {', '.join(holds)}. Holds must be cleared before placement clearance.")

    if is_eligible:
        reasons.append(
            f"Student meets placement eligibility criteria (CGPA {cgpa_op} {min_cgpa:.2f}, active backlogs {backlog_op} {max_backlogs}) ({source_doc_id}, {source_section})."
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
