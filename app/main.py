"""FastAPI application entrypoint for the University Student Services Assistant.

Provides REST API endpoints for health status, student assistance queries,
and eligibility checks.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import HealthResponse
from app.config import settings

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


if __name__ == "__main__":
    import uvicorn

    # Run the server directly when executed with `python -m app.main`
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
