import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_engine():
    """Attempt connecting to configured database (PostgreSQL), falling back to SQLite if unreachable in dev."""
    primary_url = settings.DATABASE_URL
    try:
        if primary_url.startswith("postgres://"):
            primary_url = primary_url.replace("postgres://", "postgresql://", 1)
        
        # Test connection
        test_engine = create_engine(
            primary_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 3} if "postgresql" in primary_url else {}
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Connected to Primary Database: {primary_url.split('@')[-1] if '@' in primary_url else primary_url}")
        return test_engine
    except Exception as e:
        logger.warning(
            f"Could not connect to primary database ({settings.DATABASE_URL}): {e}. "
            f"Falling back to local SQLite database ({settings.SQLITE_FALLBACK_URL})."
        )
        return create_engine(
            settings.SQLITE_FALLBACK_URL,
            connect_args={"check_same_thread": False},
            echo=False,
        )


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables."""
    # Import all models to ensure metadata registers all tables
    import backend.app.models  # noqa
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")
