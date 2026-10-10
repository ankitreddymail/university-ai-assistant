"""CLI script to ingest documents from data/documents/ into ChromaDB."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.ingestion import ingest_all_documents
from app.config import settings


def main():
    print(f"Ingesting documents from {settings.documents_dir} into ChromaDB ({settings.chroma_persist_dir})...")
    result = ingest_all_documents(
        documents_dir=settings.documents_dir,
        persist_dir=settings.chroma_persist_dir,
    )
    print(f"Status: {result['status']}")
    print(f"Documents processed: {result['documents_processed']}")
    print(f"Total chunks indexed: {result['total_chunks_indexed']}")
    print("Ingested documents:")
    for d in result["documents"]:
        synth_flag = "[SYNTHETIC]" if d["synthetic"] else "[OFFICIAL]"
        print(f"  {synth_flag} {d['title']} ({d['pages']} pages, {d['chunks']} chunks)")


if __name__ == "__main__":
    main()
