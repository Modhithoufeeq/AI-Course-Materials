"""CLI: ingest files/directories into the vector knowledge base.

Usage (from backend/, with the full runtime stack up):
    python scripts/ingest.py ../data/documents --recursive
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.services.document_service import DocumentService  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest documents into pgvector.")
    parser.add_argument("path", help="File or directory to ingest")
    parser.add_argument("--recursive", action="store_true",
                        help="Recurse into subdirectories")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    service = DocumentService(get_settings())
    results = service.ingest_path(args.path, recursive=args.recursive)

    if not results:
        print("No supported documents found.")
        return 1
    for result in results:
        doc = result.document
        print(f"[ok] {doc.filename}: {result.ingested_chunks} chunks "
              f"({doc.char_count} chars) id={doc.id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
