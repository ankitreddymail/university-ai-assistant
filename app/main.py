"""FastAPI application entrypoint for the University Student Services Assistant.

Provides REST API endpoints for:
- Health status (GET /health)
- Document ingestion (POST /ingest)
- Ingested sources listing (GET /sources)
- Authenticated student data access (GET /student/profile, /attendance, /results)
- Deterministic eligibility evaluation (POST /eligibility/check)
- Academic rule registry inspection (GET /rules)

CRITICAL SECURITY RULES:
- Student lookups strictly require the authenticated 'X-Student-Id' request header.
- Cross-student access is strictly blocked with HTTP 403 Forbidden.
- Never use a student ID from the message body for personal record lookups.
"""

from typing import Optional, List
from fastapi import FastAPI, Header, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    HealthResponse,
    IngestResponse,
    SourcesResponse,
    StudentProfile,
    AttendanceRecord,
    ResultRecord,
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    RuleRegistryEntry,
)
from app.config import settings
from app.rag.ingestion import ingest_all_documents, get_ingested_sources
from app.tools.student_data import (
    get_student_by_id,
    get_student_attendance,
    get_student_results,
    get_all_rules,
)
from app.tools.eligibility import (
    check_attendance_eligibility,
    check_exam_result_eligibility,
    check_supplementary_exam_eligibility,
    check_placement_eligibility,
)

app = FastAPI(
    title="University Student Services Assistant API",
    description="Backend API powering RAG and deterministic eligibility verification for university students.",
    version="0.1.0",
)

# Enable CORS for local Streamlit frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_authenticated_student_id(
    x_student_id: Optional[str] = Header(None, alias="X-Student-Id"),
) -> str:
    """Dependency enforcing that student identity is supplied via authenticated HTTP header."""
    if not x_student_id or not x_student_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid 'X-Student-Id' request header.",
        )
    return x_student_id.strip()


def verify_no_cross_student_access(auth_student_id: str, requested_student_id: Optional[str]) -> None:
    """Block any attempt to query or manipulate another student's records."""
    if requested_student_id and requested_student_id.strip().upper() != auth_student_id.strip().upper():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Access Denied: Cross-student record access is strictly prohibited. "
                f"Authenticated as '{auth_student_id}', but requested '{requested_student_id}'."
            ),
        )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health() -> HealthResponse:
    """Return application health status and basic metadata."""
    return HealthResponse(
        status="ok",
        app_name="University Student Services Assistant",
        version="0.1.0",
    )


@app.post("/ingest", response_model=IngestResponse, tags=["RAG"])
def ingest_documents() -> IngestResponse:
    """Ingest or refresh documents from data/documents/ into ChromaDB without server restart."""
    result = ingest_all_documents(
        documents_dir=settings.documents_dir,
        persist_dir=settings.chroma_persist_dir,
    )
    return IngestResponse(**result)


@app.get("/sources", response_model=SourcesResponse, tags=["RAG"])
def list_sources() -> SourcesResponse:
    """List all currently ingested documents and their metadata."""
    result = get_ingested_sources(persist_dir=settings.chroma_persist_dir)
    return SourcesResponse(**result)


@app.get("/student/profile", response_model=StudentProfile, tags=["Student Data"])
def get_student_profile(
    auth_student_id: str = Depends(get_authenticated_student_id),
) -> StudentProfile:
    """Fetch personal student profile strictly using the authenticated X-Student-Id header."""
    record = get_student_by_id(auth_student_id, db_path=settings.sqlite_db_path)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record not found for ID: '{auth_student_id}'.",
        )
    return StudentProfile(**record)


@app.get("/student/attendance", response_model=List[AttendanceRecord], tags=["Student Data"])
def get_student_attendance_records(
    course_code: Optional[str] = None,
    auth_student_id: str = Depends(get_authenticated_student_id),
) -> List[AttendanceRecord]:
    """Fetch course attendance records for the authenticated student."""
    # Verify student exists
    if not get_student_by_id(auth_student_id, db_path=settings.sqlite_db_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record not found for ID: '{auth_student_id}'.",
        )

    records = get_student_attendance(auth_student_id, db_path=settings.sqlite_db_path, course_code=course_code)
    return [AttendanceRecord(**r) for r in records]


@app.get("/student/results", response_model=List[ResultRecord], tags=["Student Data"])
def get_student_result_records(
    auth_student_id: str = Depends(get_authenticated_student_id),
) -> List[ResultRecord]:
    """Fetch academic examination results for the authenticated student."""
    # Verify student exists
    if not get_student_by_id(auth_student_id, db_path=settings.sqlite_db_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student record not found for ID: '{auth_student_id}'.",
        )

    records = get_student_results(auth_student_id, db_path=settings.sqlite_db_path)
    return [ResultRecord(**r) for r in records]


@app.post("/eligibility/check", response_model=EligibilityCheckResponse, tags=["Eligibility Engine"])
def evaluate_eligibility(
    req: EligibilityCheckRequest,
    auth_student_id: str = Depends(get_authenticated_student_id),
) -> EligibilityCheckResponse:
    """Deterministically evaluate student eligibility against official rules in rule_registry.
    
    Security: Strictly rejects cross-student access if student_id is passed in body.
    """
    # Guard against cross-student access attempts
    verify_no_cross_student_access(auth_student_id, req.student_id)

    service = req.service_type.strip().lower()
    db_path = settings.sqlite_db_path

    if service in ("attendance", "attendance_check"):
        outcome = check_attendance_eligibility(auth_student_id, db_path=db_path, course_code=req.course_code)
    elif service in ("exam_result", "exam", "progression"):
        outcome = check_exam_result_eligibility(auth_student_id, db_path=db_path)
    elif service in ("supplementary_exam", "supplementary", "supp"):
        outcome = check_supplementary_exam_eligibility(auth_student_id, db_path=db_path, course_code=req.course_code)
    elif service in ("placement", "placements"):
        outcome = check_placement_eligibility(auth_student_id, db_path=db_path)
    else:
        outcome = {
            "student_id": auth_student_id,
            "service_type": req.service_type,
            "is_eligible": False,
            "reasons": [
                f"Unsupported service type: '{req.service_type}'. "
                f"Supported evaluation services: attendance, exam_result, supplementary_exam, placement."
            ],
            "rule_id": None,
            "source_doc_id": None,
            "source_section": None,
        }

    return EligibilityCheckResponse(**outcome)


@app.get("/rules", response_model=List[RuleRegistryEntry], tags=["Eligibility Engine"])
def list_rules() -> List[RuleRegistryEntry]:
    """Retrieve all business rules from rule_registry for transparent verification."""
    rules = get_all_rules(settings.sqlite_db_path)
    return [RuleRegistryEntry(**r) for r in rules]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
