"""Document ingestion pipeline script to index all regulatory files in documents/."""

import os
import sys

# Ensure backend root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from services.rag_service import RAGService
from database.db import init_db


def ingest_all_documents(docs_dir=None):
    """Scan documents directory and ingest all .txt, .pdf, .docx files into RAGService."""
    docs_dir = docs_dir or getattr(Config, "KNOWLEDGE_BASE_DIR", os.path.join(BASE_DIR, "knowledge_base", "documents"))
    print(f"[Ingest] Scanning directory: {docs_dir}")

    if not os.path.exists(docs_dir):
        print(f"[Ingest] Directory does not exist: {docs_dir}")
        return 0

    rag = RAGService.get_instance()
    total_chunks = 0
    supported_extensions = (".txt", ".pdf", ".docx", ".doc")

    files = [f for f in os.listdir(docs_dir) if f.lower().endswith(supported_extensions)]
    print(f"[Ingest] Found {len(files)} document(s) to process.")

    for filename in sorted(files):
        file_path = os.path.join(docs_dir, filename)
        title = filename.replace("_", " ").rsplit(".", 1)[0].title()
        doc_type = filename.rsplit(".", 1)[1].lower()
        print(f"[Ingest] Ingesting: {filename} ({doc_type})...")
        try:
            chunks = rag.ingest_document(
                file_path=file_path,
                metadata={"title": title, "document_type": doc_type, "source": filename}
            )
            print(f"[Ingest] Indexed {chunks} chunk(s) from {filename}.")
            total_chunks += chunks
        except Exception as e:
            print(f"[Ingest] Failed to process {filename}: {e}")

    print(f"[Ingest] Ingestion completed. Total chunks indexed: {total_chunks}")
    return total_chunks


if __name__ == "__main__":
    init_db()
    ingest_all_documents()
