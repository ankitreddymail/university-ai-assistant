"""Tests for RAG PDF ingestion, metadata, duplicate prevention, and retrieval citations."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rag.ingestion import (
    extract_pages_from_file,
    extract_metadata_from_file,
    ingest_single_document,
    get_chroma_collection,
)
from app.rag.retrieval import query_knowledge_base, format_retrieved_context

DOCUMENTS_DIR = Path("data/documents")


def test_pdf_page_extraction():
    """Verify PDF pages are extracted page-by-page preserving 1-indexed numbers."""
    pdf_path = DOCUMENTS_DIR / "FEE_REFUND_POLICY.pdf"
    assert pdf_path.exists(), "FEE_REFUND_POLICY.pdf should exist in data/documents"

    pages = extract_pages_from_file(pdf_path)
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
    assert len(pages[0]["text"]) > 20

    # Multi-page PDF test
    multi_page_pdf = DOCUMENTS_DIR / "Academic Activities Calendar July -Dec 2026.pdf"
    if multi_page_pdf.exists():
        multi_pages = extract_pages_from_file(multi_page_pdf)
        assert len(multi_pages) == 2
        assert [p["page_number"] for p in multi_pages] == [1, 2]


def test_metadata_extraction_official_vs_synthetic():
    """Verify official PDFs have synthetic=False and markdown templates have synthetic=True."""
    official_pdf = DOCUMENTS_DIR / "Placement Policy 2026-07-28_002.pdf"
    assert official_pdf.exists()

    meta_official = extract_metadata_from_file(official_pdf)
    assert meta_official["synthetic"] is False
    assert meta_official["doc_version_date"] == "2026-07-28"
    assert meta_official["source_url"] == "unknown"
    assert meta_official["effective_date"] == "unknown"

    synthetic_md = DOCUMENTS_DIR / "academic_policies.md"
    assert synthetic_md.exists()

    meta_synthetic = extract_metadata_from_file(synthetic_md)
    assert meta_synthetic["synthetic"] is True
    assert meta_synthetic["source_url"] == "unknown"


def test_duplicate_ingestion_prevented(tmp_path):
    """Verify that repeatedly ingesting the same document produces no duplicate chunks."""
    test_collection = get_chroma_collection(
        persist_dir=str(tmp_path / "chroma"),
        collection_name="test_dedup_collection",
    )
    doc_path = DOCUMENTS_DIR / "FEE_REFUND_POLICY.pdf"

    # First ingestion
    result_1 = ingest_single_document(doc_path, test_collection)
    chunks_1 = result_1["chunks"]
    assert chunks_1 > 0

    count_after_first = test_collection.count()
    assert count_after_first == chunks_1

    # Second ingestion of the exact same document
    result_2 = ingest_single_document(doc_path, test_collection)
    chunks_2 = result_2["chunks"]
    assert chunks_2 == chunks_1

    count_after_second = test_collection.count()
    # Count must remain exactly the same; no duplicate chunks allowed
    assert count_after_second == count_after_first


def test_retrieval_citations(tmp_path):
    """Verify semantic retrieval returns proper citations and metadata."""
    test_persist = str(tmp_path / "chroma_retrieval")
    test_collection = get_chroma_collection(
        persist_dir=test_persist,
        collection_name="test_retrieval_collection",
    )

    doc_path = DOCUMENTS_DIR / "FEE_REFUND_POLICY.pdf"
    ingest_single_document(doc_path, test_collection)

    chunks = query_knowledge_base(
        query_text="fee refund rules and security deduction",
        top_k=2,
        persist_dir=test_persist,
        collection_name="test_retrieval_collection",
    )

    assert len(chunks) > 0
    first_chunk = chunks[0]
    assert "citation" in first_chunk
    assert "Page" in first_chunk["citation"]
    assert first_chunk["page_number"] == 1
    assert first_chunk["synthetic"] is False
    assert len(first_chunk["content"]) > 10

    # Test formatted context delimiter protection
    formatted = format_retrieved_context(chunks)
    assert "--- REFERENCE SOURCE 1:" in formatted
    assert "[Synthetic: False]" in formatted


def test_api_ingest_and_sources_endpoints():
    """Verify POST /ingest and GET /sources endpoints work via FastAPI client."""
    client = TestClient(app)

    # Ingest documents
    ingest_resp = client.post("/ingest")
    assert ingest_resp.status_code == 200
    ingest_data = ingest_resp.json()
    assert ingest_data["status"] == "success"
    assert ingest_data["documents_processed"] >= 7
    assert ingest_data["total_chunks_indexed"] > 0

    # Re-ingest to verify idempotency on server
    reingest_resp = client.post("/ingest")
    assert reingest_resp.status_code == 200
    reingest_data = reingest_resp.json()
    assert reingest_data["total_chunks_indexed"] == ingest_data["total_chunks_indexed"]

    # Verify GET /sources
    sources_resp = client.get("/sources")
    assert sources_resp.status_code == 200
    sources_data = sources_resp.json()
    assert sources_data["total_documents"] >= 7
    source_titles = [s["title"].lower() for s in sources_data["sources"]]
    assert any("refund" in t or "fee" in t for t in source_titles)
