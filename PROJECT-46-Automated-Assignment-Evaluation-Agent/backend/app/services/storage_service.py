import os
import shutil
import uuid
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from backend.app.core.config import settings
from backend.app.core.errors import AppException


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".py", ".java", ".cpp", ".c", ".js"}
MAX_FILE_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class StorageService:
    def __init__(self, upload_dir: str = settings.UPLOAD_DIRECTORY):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, file: UploadFile) -> str:
        """Validate file extension and return sanitized extension."""
        if not file.filename:
            raise AppException(status_code=400, detail="Uploaded file has no filename.")
        
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(ALLOWED_EXTENSIONS)
            raise AppException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {allowed}"
            )
        return ext

    async def save_upload_file(self, file: UploadFile, subfolder: str = "submissions") -> Tuple[str, str, int, str]:
        """
        Save uploaded file to disk securely.
        Returns: (stored_file_path, original_filename, file_size_bytes, file_extension)
        """
        ext = self.validate_file(file)
        
        target_dir = self.upload_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        unique_filename = f"{uuid.uuid4().hex}_{Path(file.filename).name}"
        destination_path = target_dir / unique_filename
        
        size = 0
        with open(destination_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                size += len(chunk)
                if size > MAX_FILE_SIZE_BYTES:
                    destination_path.unlink(missing_ok=True)
                    raise AppException(
                        status_code=413,
                        detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                    )
                buffer.write(chunk)
                
        return str(destination_path), file.filename, size, ext.replace(".", "")


storage_service = StorageService()
