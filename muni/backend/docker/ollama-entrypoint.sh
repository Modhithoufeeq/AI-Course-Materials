#!/bin/sh
# ─────────────────────────────────────────────────────────────────────────────
# Ollama container entrypoint.
# Starts the Ollama server and pre-pulls the free open-source models used by
# the platform. Override OLLAMA_LLM_MODEL / OLLAMA_EMBED_MODEL to use other
# free models (e.g. qwen2.5:7b, llama3.1:8b, nomic-embed-text).
# ─────────────────────────────────────────────────────────────────────────────
set -e

ollama serve &
OLLAMA_PID=$!

# Wait for the server socket to be ready
for i in $(seq 1 60); do
  if curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "==> Pulling LLM model: ${OLLAMA_LLM_MODEL:-llama3.1}"
ollama pull "${OLLAMA_LLM_MODEL:-llama3.1}" || echo "WARN: could not pull ${OLLAMA_LLM_MODEL:-llama3.1}"

echo "==> Pulling embedding model: ${OLLAMA_EMBED_MODEL:-nomic-embed-text}"
ollama pull "${OLLAMA_EMBED_MODEL:-nomic-embed-text}" || echo "WARN: could not pull ${OLLAMA_EMBED_MODEL:-nomic-embed-text}"

echo "==> Ollama ready on :11434"
wait "$OLLAMA_PID"