"""Pydantic v2 data models and request/response schemas.

Defines schemas aligned strictly with Annex C of the HCLTech hackathon specification.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="ok", description="Current service health status")
    app_name: str = Field(default="University Student Services Assistant", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")


class StudentProfile(BaseModel):
    """Schema representing a student record (Annex C)."""
    student_id: str
    full_name: str
    programme: str
    batch_year: int
    current_semester: int
    cgpa: float = Field(..., ge=0.0, le=10.0, description="Cumulative GPA on 0.0-10.0 scale")
    active_backlogs: int = Field(default=0, ge=0)
    email: Optional[str] = None
    holds: List[str] = Field(default_factory=list)


class CourseRecord(BaseModel):
    """Schema representing a university course (Annex C)."""
    course_code: str
    course_name: str
    programme: str
    semester: int
    credits: int


class AttendanceRecord(BaseModel):
    """Schema representing course attendance (Annex C)."""
    student_id: str
    course_code: str
    classes_held: int
    classes_attended: int
    attendance_percentage: Optional[float] = None


class ResultRecord(BaseModel):
    """Schema representing semester exam result (Annex C)."""
    student_id: str
    course_code: str
    exam_session: str
    exam_type: str
    internal_marks: float
    external_marks: float
    total_marks: float
    max_marks: float
    result: str  # 'Pass', 'Fail'


class RuleRegistryEntry(BaseModel):
    """Schema for academic business rules in rule_registry (Annex C)."""
    rule_id: str
    description: str
    parameter: str
    operator: str
    value: str
    scope_programmes: str
    scope_batches: str
    effective_from: str
    effective_to: str
    source_doc_id: str
    source_section: str


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
    source_doc_id: Optional[str] = None
    source_section: Optional[str] = None


class IngestedDocSummary(BaseModel):
    """Summary of a single ingested document."""
    doc_id: str
    title: str
    pages: int
    chunks: int
    synthetic: bool


class IngestResponse(BaseModel):
    """Response schema for POST /ingest endpoint."""
    status: str = "success"
    documents_processed: int
    total_chunks_indexed: int
    documents: List[IngestedDocSummary] = Field(default_factory=list)


class SourceItem(BaseModel):
    """Metadata item for an ingested document source."""
    doc_id: str
    title: str
    total_pages: int
    total_chunks: int
    doc_version_date: str
    effective_date: str
    source_url: str
    synthetic: bool


class SourcesResponse(BaseModel):
    """Response schema for GET /sources endpoint."""
    total_documents: int
    sources: List[SourceItem] = Field(default_factory=list)
