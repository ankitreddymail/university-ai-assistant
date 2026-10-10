"""Rule Resolution Registry Tool.

Resolves service categories (attendance, exam_result, supplementary_exam, placement)
and routes them to deterministic evaluation functions backed by SQLite rule_registry.
"""

from typing import Dict, Any, Optional
from app.tools.eligibility import (
    check_attendance_eligibility,
    check_exam_result_eligibility,
    check_supplementary_exam_eligibility,
    check_placement_eligibility,
)

# Registry mapping service category strings to eligibility functions
ELIGIBILITY_ROUTERS = {
    "attendance": check_attendance_eligibility,
    "exam_result": check_exam_result_eligibility,
    "exam": check_exam_result_eligibility,
    "supplementary_exam": check_supplementary_exam_eligibility,
    "supplementary": check_supplementary_exam_eligibility,
    "placement": check_placement_eligibility,
}


def resolve_and_evaluate_rule(
    service_type: str,
    student_id: str,
    db_path: str,
    course_code: Optional[str] = None,
) -> Dict[str, Any]:
    """Look up evaluator for service_type and execute rule check against the database."""
    normalized_service = service_type.strip().lower()

    if normalized_service in ("attendance", "supplementary_exam", "supplementary"):
        evaluator = ELIGIBILITY_ROUTERS.get(normalized_service)
        if evaluator:
            return evaluator(student_id=student_id, db_path=db_path, course_code=course_code)

    evaluator = ELIGIBILITY_ROUTERS.get(normalized_service)
    if not evaluator:
        return {
            "student_id": student_id,
            "service_type": service_type,
            "is_eligible": False,
            "reasons": [f"No predefined rule evaluator registered for service: '{service_type}'."],
            "rule_id": None,
            "source_document": None,
            "clause": None,
        }

    return evaluator(student_id=student_id, db_path=db_path)
