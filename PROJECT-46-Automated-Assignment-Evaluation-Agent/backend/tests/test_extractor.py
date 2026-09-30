import pytest
import tempfile
from pathlib import Path
from backend.app.services.document_extractor import document_extractor
from backend.app.core.errors import DocumentExtractionException


def test_plaintext_extraction():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("Hello World! This is a test assignment submission document.\nIt contains multiple lines.")
        temp_path = f.name

    try:
        res = document_extractor.extract_text(temp_path, "txt")
        assert res["word_count"] == 13
        assert "Hello World!" in res["text"]
        assert len(res["preview"]) > 0
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_empty_document_raises_extraction_exception():
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("    \n\n  \t ")
        temp_path = f.name

    try:
        with pytest.raises(DocumentExtractionException):
            document_extractor.extract_text(temp_path, "txt")
    finally:
        Path(temp_path).unlink(missing_ok=True)
