import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.ingestion import get_ingested_sources
from app.config import settings


def display_sources():
    data = get_ingested_sources(persist_dir=settings.chroma_persist_dir)
    print(f"\nIngested Document Sources ({data['total_documents']} total):")
    for s in data["sources"]:
        synth_label = "[SYNTHETIC]" if s["synthetic"] else "[OFFICIAL]"
        print(
            f"  {synth_label} {s['title']}\n"
            f"    Doc ID: {s['doc_id']} | Pages: {s['total_pages']} | Chunks: {s['total_chunks']}\n"
            f"    Version/Date: {s['doc_version_date']} | Effective: {s['effective_date']} | URL: {s['source_url']}"
        )


if __name__ == "__main__":
    display_sources()
