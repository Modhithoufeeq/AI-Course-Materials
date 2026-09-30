"""Unit tests for the dependency-free text chunker."""

import pytest

from app.core.ingestion.chunker import split_text


def test_empty_text_returns_no_chunks() -> None:
    assert split_text("") == []
    assert split_text("   \n \n  ") == []


def test_short_text_is_a_single_chunk() -> None:
    chunks = split_text("Hello world, this is a short document.")
    assert chunks == ["Hello world, this is a short document."]


def test_invalid_chunk_size_raises() -> None:
    with pytest.raises(ValueError):
        split_text("some text", chunk_size=0)


def test_paragraphs_packed_up_to_chunk_size() -> None:
    paragraph = "A" * 100
    text = "\n\n".join(paragraph for _ in range(10))
    chunks = split_text(text, chunk_size=256, chunk_overlap=0)
    assert len(chunks) >= 3
    assert all(len(c) <= 256 for c in chunks)


def test_overlap_carries_tail_context() -> None:
    p1 = "P1-" + "x" * 200
    p2 = "P2-" + "y" * 200
    chunks = split_text(f"{p1}\n\n{p2}", chunk_size=256, chunk_overlap=32)
    assert len(chunks) == 2
    assert chunks[1].startswith(chunks[0][-32:])
    assert all(len(c) <= 256 for c in chunks)


def test_oversized_paragraph_is_split_on_words() -> None:
    text = " ".join(["word"] * 500)  # ~2500 chars
    chunks = split_text(text, chunk_size=400, chunk_overlap=50)
    assert len(chunks) >= 5
    assert all(len(c) <= 400 for c in chunks)
    # Reconstruction should cover all words.
    joined = " ".join(chunks)
    assert joined.count("word") >= 500
