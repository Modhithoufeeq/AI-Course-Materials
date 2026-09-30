"""Centralised, typed application settings (12-factor style).

Every value has a safe default so the app boots even with no environment at
all; production deployments override via ``backend/.env`` or real env vars.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _default_ingest_dir() -> Path:
    return _REPO_ROOT / "data" / "documents"


class Settings(BaseSettings):
    """All runtime configuration for the backend."""

    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")

    # ── App / API ────────────────────────────────────────────────────────────
    APP_NAME: str = "Document Search Platform"
    ENVIRONMENT: str = "development"  # development | staging | production | test
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
    ]

    # ── Ollama (free, local models) ──────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "llama3.1"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_REQUEST_TIMEOUT: float = 180.0

    # ── Embeddings ───────────────────────────────────────────────────────────
    EMBEDDING_DIM: int = 768  # nomic-embed-text → 768

    # ── PostgreSQL / pgvector ────────────────────────────────────────────────
    PGVECTOR_HOST: str = "localhost"
    PGVECTOR_PORT: int = 5432
    PGVECTOR_DATABASE: str = "ragdb"
    PGVECTOR_USER: str = "postgres"
    PGVECTOR_PASSWORD: str = "postgres"
    PGVECTOR_TABLE: str = "documents"  # chunk/vector table (managed by llama-index)
    PGVECTOR_METADATA_TABLE: str = "document_meta"

    # ── Retrieval tuning ─────────────────────────────────────────────────────
    RETRIEVAL_TOP_K: int = 6
    COMPRESSION_ENABLED: bool = True
    COMPRESSION_CONTEXT_WINDOW: int = 4  # passages kept after LLM re-ranking
    RAG_TEMPERATURE: float = 0.1

    # ── Chunking ─────────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 200

    # ── Agentic pipeline (CrewAI) ────────────────────────────────────────────
    AGENTIC_MODE: bool = True  # false → plain LlamaIndex-style RAG
    CREW_VERBOSE: bool = False

    # ── Arize Phoenix observability (OpenTelemetry) ──────────────────────────
    TRACING_ENABLED: bool = True
    PHOENIX_COLLECTOR_ENDPOINT: str = "http://localhost:6006"
    PHOENIX_UI_URL: str = "http://localhost:6006"

    # ── Ingestion ────────────────────────────────────────────────────────────
    INGEST_DIR: Path = Field(default_factory=_default_ingest_dir)
    AUTO_INGEST_ON_STARTUP: bool = False
    MAX_FILE_SIZE_MB: int = 50

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _parse_origins(cls, value: object) -> object:
        """Accept a JSON list (as in .env files) or a comma-separated string."""
        import json

        if isinstance(value, str):
            text = value.strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return [origin.strip() for origin in text.split(",") if origin.strip()]
        return value

    @property
    def pg_conninfo(self) -> str:
        """libpq connection string for psycopg."""
        return (
            f"host={self.PGVECTOR_HOST} port={self.PGVECTOR_PORT} "
            f"dbname={self.PGVECTOR_DATABASE} user={self.PGVECTOR_USER} "
            f"password={self.PGVECTOR_PASSWORD}"
        )

    @property
    def sqlalchemy_url(self) -> str:
        """SQLAlchemy URL used by llama-index's PGVectorStore."""
        return (
            f"postgresql+psycopg://{self.PGVECTOR_USER}:{self.PGVECTOR_PASSWORD}"
            f"@{self.PGVECTOR_HOST}:{self.PGVECTOR_PORT}/{self.PGVECTOR_DATABASE}"
        )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton (loads backend/.env once)."""
    load_dotenv(Path.cwd() / ".env")
    return Settings()
