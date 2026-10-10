"""Audit Logging and Transparency Module.

Logs user interactions, rule evaluations, and retrieved sources
to a local JSON-lines log file or SQLite audit table for interview demonstration
and transparency verification.
"""

import json
import time
from typing import Dict, Any, Optional
from pathlib import Path


def log_interaction(
    question: str,
    answer: str,
    student_id: Optional[str] = None,
    sources: Optional[list] = None,
    applied_rules: Optional[list] = None,
    log_dir: str = "reports"
) -> Dict[str, Any]:
    """Append a structured audit entry to the audit log."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    audit_file = Path(log_dir) / "audit_log.jsonl"

    entry = {
        "timestamp": time.time(),
        "student_id": student_id,
        "question": question,
        "answer": answer,
        "sources": sources or [],
        "applied_rules": applied_rules or [],
    }

    with open(audit_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry
