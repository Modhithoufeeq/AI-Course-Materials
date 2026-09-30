"""Pure-python, deterministic, paragraph-aware text chunking.

Kept dependency-free on purpose: it is a pure function, fully unit-testable,
and avoids pulling LlamaIndex (or a tokenizer model) into the request path.
"""

from __future__ import annotations

import re

_PARAGRAPH_BREAK = re.compile(r"\n\s*\n")
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")


def split_text(
    text: str,
    *,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
) -> list[str]:
    """Split document text into overlapping, paragraph-aware chunks.

    Strategy:
      * normalise line endings and split on paragraph boundaries;
      * greedily pack paragraphs into chunks up to ``chunk_size`` chars;
      * oversized paragraphs are split on sentence, then word boundaries,
        always carrying ``chunk_overlap`` characters of context forward.
    """
    if not text:
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap >= chunk_size:
        chunk_overlap = max(0, chunk_size - 1)

    normalised = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalised:
        return []

    chunks: list[str] = []
    current = ""

    for raw_paragraph in _PARAGRAPH_BREAK.split(normalised):
        paragraph = raw_paragraph.strip()
        if not paragraph:
            continue

        if len(paragraph) <= chunk_size:
            joined = f"{current}\n\n{paragraph}" if current else paragraph
            if len(joined) <= chunk_size:
                current = joined
            else:
                if current:
                    chunks.append(current)
                current = paragraph
            continue

        # Oversized paragraph → sentence/word level splitting.
        if current:
            chunks.append(current)
            current = ""
        sentences = [s.strip() for s in _SENTENCE_BREAK.split(paragraph) if s.strip()]
        buf = ""
        for sentence in sentences:
            if len(sentence) > chunk_size:
                if buf:
                    chunks.append(buf)
                    buf = ""
                chunks.extend(_split_long_words(sentence, chunk_size, chunk_overlap))
                continue
            joined = f"{buf} {sentence}".strip() if buf else sentence
            if len(joined) <= chunk_size:
                buf = joined
            else:
                if buf:
                    chunks.append(buf)
                buf = sentence
        if buf:
            current = buf

    if current:
        chunks.append(current)

    if len(chunks) <= 1:
        return chunks

    # Carry a tail of the previous chunk into the next one when it fits.
    merged = [chunks[0]]
    for chunk in chunks[1:]:
        tail = merged[-1][-chunk_overlap:]
        candidate = f"{tail} {chunk}".strip() if tail else chunk
        merged.append(candidate if len(candidate) <= chunk_size else chunk)
    return merged


def _split_long_words(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split a single very long passage on word boundaries with overlap."""
    words = text.split()
    pieces: list[str] = []
    buf: list[str] = []
    buf_len = 0

    for word in words:
        extra = len(word) + (1 if buf else 0)
        if buf and buf_len + extra > chunk_size:
            pieces.append(" ".join(buf))
            # carry trailing words that fit in the overlap window
            carry: list[str] = []
            carry_len = 0
            for prev in reversed(buf):
                add = len(prev) + (1 if carry else 0)
                if carry_len + add > overlap:
                    break
                carry.insert(0, prev)
                carry_len += add
            buf = carry
            buf_len = carry_len
        buf.append(word)
        buf_len += len(word) + (1 if len(buf) > 1 else 0)

    if buf:
        pieces.append(" ".join(buf))
    return [p for p in pieces if p.strip()]
