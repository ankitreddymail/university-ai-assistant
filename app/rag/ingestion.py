"""Document Ingestion Module for RAG Knowledge Base.

Responsible for:
1. Loading policy markdown / text files from data/documents/.
2. Splitting documents into manageable text chunks.
3. Generating vector embeddings using sentence-transformers (all-MiniLM-L6-v2).
4. Persisting embeddings and metadata into ChromaDB.
"""

from typing import List, Dict, Any
from pathlib import Path


def load_policy_documents(documents_dir: str) -> List[Dict[str, str]]:
    """Scan documents directory and load text files into memory.
    
    Returns a list of dictionaries with 'doc_name' and 'content'.
    """
    doc_path = Path(documents_dir)
    documents = []

    if not doc_path.exists():
        # Directory does not exist yet; return empty list gracefully
        return documents

    for file_path in doc_path.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            documents.append({
                "doc_name": file_path.name,
                "content": f.read()
            })

    return documents


def ingest_documents_to_chroma(documents_dir: str, persist_dir: str) -> int:
    """Read university policy documents and index them in persistent ChromaDB.
    
    Full implementation will be added during RAG module phase.
    """
    docs = load_policy_documents(documents_dir)
    # Placeholder: indexing logic will be integrated in subsequent phase
    return len(docs)
