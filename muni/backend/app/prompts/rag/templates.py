"""Grounded RAG answer prompt."""

from __future__ import annotations

from app.schemas.query import SourceRef

SYSTEM_PROMPT = """\
You are a precise research assistant answering questions ONLY from the \
provided context.

Rules:
1. Base every claim on the context below. Never use outside knowledge.
2. If the context does not contain the answer, reply exactly: \
"I could not find this information in the available documents." and do not guess.
3. Cite sources inline like [1], [2] referring to the numbered context passages.
4. Answer in the same language as the question.
5. Keep the answer concise (<= 180 words); use short paragraphs or bullet \
points when helpful.
"""


def format_context(sources: list[SourceRef]) -> str:
    lines = [f"[{s.index}] (from: {s.filename}) {s.text}" for s in sources]
    return "\n\n".join(lines)


def build_answer_prompt(question: str, sources: list[SourceRef]) -> str:
    context = format_context(sources) or "(no relevant context retrieved)"
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"===== CONTEXT =====\n{context}\n\n"
        f"===== QUESTION =====\n{question}\n\n"
        f"===== ANSWER ====="
    )
