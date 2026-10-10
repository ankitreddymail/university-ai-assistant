"""FastAPI application entrypoint for the University Student Services Assistant.

Provides REST API endpoints for:
- Health status (GET /health)
- Document ingestion (POST /ingest)
- Ingested sources listing (GET /sources)
- Student assistance queries and eligibility checks
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import HealthResponse, IngestResponse, SourcesResponse
from app.config import settings
from app.rag.ingestion import ingest_all_documents, get_ingested_sources

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


if __name__ == "__main__":
    import uvicorn

    # Run the server directly when executed with `python -m app.main`
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
