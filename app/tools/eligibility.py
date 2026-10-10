"""Deterministic Student Eligibility Evaluation Tool.

Evaluates student records against university academic criteria (e.g., graduation,
academic honors, credit overload, financial aid standing) using pure Python logic.
"""

from typing import Dict, Any, List, Tuple


def check_graduation_eligibility(student: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Determine if a student meets graduation criteria.
    
    Standard criteria:
    - Minimum 120 completed credits
    - Minimum GPA 2.0
    - No active financial or administrative holds
    """
    reasons = []
    credits_completed = student.get("credits_completed", 0)
    gpa = student.get("gpa", 0.0)
    holds = student.get("holds", [])

    if credits_completed < 120:
        reasons.append(f"Insufficient credits: {credits_completed}/120 required.")
    if gpa < 2.0:
        reasons.append(f"GPA {gpa:.2f} is below the required 2.00 threshold.")
    if holds:
        reasons.append(f"Active holds detected: {', '.join(holds)}.")

    is_eligible = len(reasons) == 0
    if is_eligible:
        reasons.append("Student meets all graduation requirements.")

    return is_eligible, reasons


def check_dean_list_eligibility(student: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Determine Dean's Honor List eligibility (GPA >= 3.50, no disciplinary holds)."""
    reasons = []
    gpa = student.get("gpa", 0.0)
    holds = student.get("holds", [])

    if gpa < 3.50:
        reasons.append(f"GPA {gpa:.2f} is below Dean's list threshold of 3.50.")
    if "disciplinary" in [h.lower() for h in holds]:
        reasons.append("Disciplinary hold disqualifies student from honors.")

    is_eligible = len(reasons) == 0
    if is_eligible:
        reasons.append("Student qualifies for Dean's Honor List.")

    return is_eligible, reasons
