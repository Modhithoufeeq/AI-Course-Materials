import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Information
    PROJECT_NAME: str = "Automated Assignment Evaluation Agent"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["*"]

    # Security
    SECRET_KEY: str = "eval-agent-dev-secret-key-super-secure-32chars-min-jwt-auth"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/assignment_eval_db"
    SQLITE_FALLBACK_URL: str = "sqlite:///./data/assignment_eval.db"

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_MODE: str = "local"  # "local" or "server"

    # Storage
    UPLOAD_DIRECTORY: str = "./data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # LLM Providers
    LLM_PROVIDER: str = "gemini"  # "gemini", "openai", "anthropic", "mock_deterministic"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "gemini-1.5-flash"

    # Originality Analysis Thresholds
    SIMILARITY_THRESHOLD_LOW: float = 0.20
    SIMILARITY_THRESHOLD_MEDIUM: float = 0.45
    SIMILARITY_THRESHOLD_HIGH: float = 0.70

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
