import re
from pathlib import Path
from typing import Dict, Any
from pypdf import PdfReader
import docx
from backend.app.core.errors import DocumentExtractionException


class DocumentExtractorService:
    """Service to safely extract text from multiple document formats (PDF, DOCX, TXT, MD, Code)."""

    def extract_text(self, file_path: str, file_type: str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise DocumentExtractionException(f"File not found on disk at {file_path}")

        file_type = file_type.lower().replace(".", "")
        
        try:
            if file_type == "pdf":
                raw_text = self._extract_pdf(path)
            elif file_type in ("docx", "doc"):
                raw_text = self._extract_docx(path)
            elif file_type in ("txt", "md", "py", "java", "cpp", "c", "js", "html", "json"):
                raw_text = self._extract_plaintext(path)
            else:
                # Fallback to plain text attempt
                raw_text = self._extract_plaintext(path)

            cleaned_text = self._clean_text(raw_text)
            
            if not cleaned_text or len(cleaned_text.strip()) == 0:
                raise DocumentExtractionException(
                    "The document appears to be empty or contains no extractable text (e.g. scanned image without OCR)."
                )

            words = cleaned_text.split()
            word_count = len(words)
            char_count = len(cleaned_text)

            return {
                "text": cleaned_text,
                "word_count": word_count,
                "character_count": char_count,
                "preview": cleaned_text[:300] + ("..." if len(cleaned_text) > 300 else ""),
            }

        except DocumentExtractionException:
            raise
        except Exception as e:
            raise DocumentExtractionException(f"Failed to process {file_type.upper()} document: {str(e)}")

    def _extract_pdf(self, path: Path) -> str:
        extracted_pages = []
        try:
            reader = PdfReader(str(path))
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(page_text.strip())
            return "\n\n".join(extracted_pages)
        except Exception as e:
            raise DocumentExtractionException(f"Corrupt or encrypted PDF file: {str(e)}")

    def _extract_docx(self, path: Path) -> str:
        try:
            doc = docx.Document(str(path))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            
            # Also extract text inside tables if any
            table_texts = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        table_texts.append(row_text)
            
            full_text = "\n\n".join(paragraphs + table_texts)
            return full_text
        except Exception as e:
            raise DocumentExtractionException(f"Invalid DOCX structure: {str(e)}")

    def _extract_plaintext(self, path: Path) -> str:
        encodings_to_try = ["utf-8", "latin-1", "utf-16", "cp1252"]
        for enc in encodings_to_try:
            try:
                with open(path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise DocumentExtractionException("Failed to decode text document using supported character encodings.")

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        # Normalize carriage returns and non-breaking spaces
        text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
        # Remove null bytes or weird control characters
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
        # Collapse multiple empty lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


document_extractor = DocumentExtractorService()
