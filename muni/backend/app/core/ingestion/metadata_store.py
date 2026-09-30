"""PostgreSQL metadata table (``document_meta``) managed with psycopg."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.core.config import Settings
from app.core.errors import DependencyUnavailableError
from app.schemas.document import DocumentMeta

logger = logging.getLogger(__name__)

_SCHEMA_TEMPLATE = """
CREATE TABLE IF NOT EXISTS {table} (
    id           TEXT        PRIMARY KEY,
    filename     TEXT        NOT NULL,
    content_type TEXT        NOT NULL DEFAULT 'application/octet-stream',
    source       TEXT        NOT NULL DEFAULT '',
    status       TEXT        NOT NULL DEFAULT 'indexed',
    char_count   INTEGER     NOT NULL DEFAULT 0,
    chunk_count  INTEGER     NOT NULL DEFAULT 0,
    extra        JSONB       NOT NULL DEFAULT '{{}}'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


class MetadataStore:
    """CRUD + health checks for the document metadata table."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def _table(self) -> str:
        return self.settings.PGVECTOR_METADATA_TABLE

    @contextmanager
    def _cursor(self):
        try:
            with psycopg.connect(self.settings.pg_conninfo) as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    yield cur
        except psycopg.OperationalError as exc:
            raise DependencyUnavailableError(
                detail=f"PostgreSQL unavailable: {exc}"
            ) from exc

    def init_schema(self) -> None:
        with self._cursor() as cur:
            cur.execute(_SCHEMA_TEMPLATE.format(table=self._table))

    def upsert(self, meta: DocumentMeta) -> None:
        with self._cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {self._table}
                    (id, filename, content_type, source, status,
                     char_count, chunk_count, extra, created_at, updated_at)
                VALUES (%(id)s, %(filename)s, %(content_type)s, %(source)s, %(status)s,
                        %(char_count)s, %(chunk_count)s, %(extra)s, %(created_at)s, %(updated_at)s)
                ON CONFLICT (id) DO UPDATE SET
                    filename = EXCLUDED.filename,
                    content_type = EXCLUDED.content_type,
                    source = EXCLUDED.source,
                    status = EXCLUDED.status,
                    char_count = EXCLUDED.char_count,
                    chunk_count = EXCLUDED.chunk_count,
                    extra = EXCLUDED.extra,
                    updated_at = now()
                """,
                {
                    "id": meta.id,
                    "filename": meta.filename,
                    "content_type": meta.content_type,
                    "source": meta.extra.get("source", ""),
                    "status": meta.status,
                    "char_count": meta.char_count,
                    "chunk_count": meta.chunk_count,
                    "extra": meta.extra,
                    "created_at": meta.created_at,
                    "updated_at": meta.updated_at,
                },
            )

    def list(self, page: int = 1, page_size: int = 20) -> tuple[list[DocumentMeta], int]:
        with self._cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total FROM {self._table}")
            total = int(cur.fetchone()["total"])
            cur.execute(
                f"SELECT * FROM {self._table} ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (page_size, (page - 1) * page_size),
            )
            return [self._row_to_meta(row) for row in cur.fetchall()], total

    def get(self, doc_id: str) -> DocumentMeta | None:
        with self._cursor() as cur:
            cur.execute(f"SELECT * FROM {self._table} WHERE id = %s", (doc_id,))
            row = cur.fetchone()
        return self._row_to_meta(row) if row else None

    def delete(self, doc_id: str) -> bool:
        with self._cursor() as cur:
            cur.execute(f"DELETE FROM {self._table} WHERE id = %s", (doc_id,))
            return cur.rowcount > 0

    def health(self) -> bool:
        try:
            with self._cursor() as cur:
                cur.execute("SELECT 1")
            return True
        except Exception:  # noqa: BLE001 — health checks must never raise
            return False

    @staticmethod
    def _row_to_meta(row: dict[str, Any]) -> DocumentMeta:
        created: datetime = row["created_at"]
        updated: datetime = row["updated_at"]
        return DocumentMeta(
            id=row["id"],
            filename=row["filename"],
            content_type=row.get("content_type") or "application/octet-stream",
            char_count=row.get("char_count", 0),
            chunk_count=row.get("chunk_count", 0),
            status=row.get("status", "indexed"),
            created_at=created,
            updated_at=updated,
            extra=row.get("extra") or {},
        )
