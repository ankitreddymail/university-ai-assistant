"""Rule Resolution Registry Tool.

Resolves service categories (graduation, honors, course overload) and maps them
to the appropriate deterministic rule evaluation functions.
"""

from typing import Dict, Any, Tuple, List, Callable
from app.tools.eligibility import check_graduation_eligibility, check_dean_list_eligibility

# Simple registry dictionary mapping service keywords to rule functions
RULE_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Tuple[bool, List[str]]]] = {
    "graduation": check_graduation_eligibility,
    "deans_list": check_dean_list_eligibility,
    "honors": check_dean_list_eligibility,
}


def resolve_and_evaluate_rule(service_name: str, student_record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Look up rule evaluator for service_name and run evaluation on student_record."""
    normalized_service = service_name.strip().lower()
    evaluator = RULE_REGISTRY.get(normalized_service)

    if not evaluator:
        return False, [f"No predefined rule evaluator registered for service: '{service_name}'."]

    return evaluator(student_record)
