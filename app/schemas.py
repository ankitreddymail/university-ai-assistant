"""Pydantic v2 data models and request/response schemas.

Defines simple, clear schemas for API endpoints and internal data handling.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="ok", description="Current service health status")
    app_name: str = Field(default="University Student Services Assistant", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")


class StudentProfile(BaseModel):
    """Schema representing a student's basic record."""
    student_id: str
    full_name: str
    email: str
    major: str
    gpa: float
    credits_completed: int
    standing: str  # e.g., Freshman, Sophomore, Junior, Senior
    holds: List[str] = Field(default_factory=list)


class QueryRequest(BaseModel):
    """User query request submitted to the assistant."""
    student_id: Optional[str] = Field(default=None, description="Optional student ID for personalized answers")
    question: str = Field(..., min_length=2, description="Student inquiry or service question")


class QueryResponse(BaseModel):
    """Assistant final response schema."""
    question: str
    answer: str
    sources: List[str] = Field(default_factory=list, description="Policy documents or sources referenced")
    student_id: Optional[str] = None
    applied_rules: List[str] = Field(default_factory=list, description="Rules evaluated during answering")


class EligibilityCheckRequest(BaseModel):
    """Request schema for evaluating student eligibility for a specific service."""
    student_id: str
    service_type: str  # e.g., 'graduation', 'financial_aid', 'course_overload'


class EligibilityCheckResponse(BaseModel):
    """Response schema detailing eligibility outcome and reasons."""
    student_id: str
    service_type: str
    is_eligible: bool
    reasons: List[str] = Field(default_factory=list)
