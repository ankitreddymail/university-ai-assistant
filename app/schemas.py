"""Pydantic v2 data models and request/response schemas.

Defines simple, clear schemas for API endpoints and internal data handling
aligned with Annex C and the hackathon specifications.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="ok", description="Current service health status")
    app_name: str = Field(default="University Student Services Assistant", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")


class StudentProfile(BaseModel):
    """Schema representing a student's academic record (Annex C)."""
    student_id: str
    full_name: str
    email: str
    programme: str
    batch: str
    current_semester: int
    cgpa: float = Field(..., ge=0.0, le=10.0, description="Cumulative GPA on 0.0-10.0 scale")
    standing: str  # e.g., 'Active', 'Good Standing', 'On Probation'
    holds: List[str] = Field(default_factory=list)


class CourseRecord(BaseModel):
    """Schema representing a university course."""
    course_code: str
    course_name: str
    programme: str
    semester: int
    credits: int
    instructor: str


class AttendanceRecord(BaseModel):
    """Schema representing student attendance in a course."""
    student_id: str
    course_code: str
    classes_attended: int
    total_classes: int
    attendance_percentage: float = Field(..., ge=0.0, le=100.0)


class ResultRecord(BaseModel):
    """Schema representing semester course results."""
    student_id: str
    course_code: str
    semester: int
    grade: str
    grade_points: float = Field(..., ge=0.0, le=10.0)
    credits: int
    status: str  # 'Pass', 'Fail', 'Supplementary'


class RuleRegistryEntry(BaseModel):
    """Schema for academic business rules sourced from policy documents."""
    rule_id: str
    rule_category: str  # e.g., 'attendance', 'exam_result', 'supplementary_exam', 'placement'
    description: str
    parameter_name: str
    parameter_value: str
    source_document: str
    clause: str


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
    service_type: str  # e.g., 'attendance', 'exam_result', 'supplementary_exam', 'placement'
    course_code: Optional[str] = Field(default=None, description="Optional course code for course-specific checks")


class EligibilityCheckResponse(BaseModel):
    """Response schema detailing eligibility outcome, reasons, and policy rule trace."""
    student_id: str
    service_type: str
    is_eligible: bool
    reasons: List[str] = Field(default_factory=list)
    rule_id: Optional[str] = None
    source_document: Optional[str] = None
    clause: Optional[str] = None
