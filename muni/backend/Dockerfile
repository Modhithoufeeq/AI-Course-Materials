# ─────────────────────────────────────────────────────────────────────────────
# Document Search Platform — backend image
# Python 3.11-slim + required system libraries for Docling (PDF) / psycopg
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        libmagic1 \
        poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Application source
COPY app ./app
COPY evaluation ./evaluation
COPY scripts ./scripts
COPY docker/ollama-entrypoint.sh ./docker/ollama-entrypoint.sh

# Data mount points (documents to ingest, evaluation reports)
RUN mkdir -p /data/documents /data/reports /app/prompts
VOLUME ["/data/documents", "/data/reports"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]