"""Shared text-analysis tools used by the evaluation agents.

Everything here is dependency-free (stdlib only) so the whole project can run
straight from a fresh Colab runtime without any `pip install`.
"""

from __future__ import annotations

import math
import re
from typing import Iterable, List

_WORD_RE = re.compile(r"[a-zA-Z0-9']+")


def tokenize(text: str) -> List[str]:
    """Split text into lowercase word tokens."""
    return list(re.findall(_WORD_RE, (text or "").lower()))


def word_count(text: str) -> int:
    return len(tokenize(text))


def sentence_count(text: str) -> int:
    raw = (text or "").strip()
    if not raw:
        return 0
    chunks = re.split(r"(?<=[.!?])\s+", raw)
    return len([c for c in chunks if c.strip()])


def unique_keywords(text: str) -> List[str]:
    seen = set()
    out = []
    for word in tokenize(text):
        if len(word) < 3:
            continue
        if word in seen:
            continue
        seen.add(word)
        out.append(word)
    return out


def keyword_coverage(text: str, keywords: Iterable[str]) -> dict:
    """Ratio of provided keywords that actually appear in the text."""
    tokens = set(tokenize(text))
    keywords = [k for k in (keywords or []) if k]
    matched = [k for k in keywords if k in tokens]
    coverage = (len(matched) / len(keywords)) if keywords else 0.0
    return {
        "matched": matched,
        "missing": [k for k in keywords if k not in tokens],
        "coverage": round(coverage, 4),
    }


def extract_evidence(text: str, keywords: Iterable[str], max_chars: int = 240) -> str:
    """Return the sentence that best covers the provided keywords."""
    keywords = {k.lower() for k in (keywords or [])}
    sentences = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    best = ""
    best_score = -1.0
    for sentence in sentences:
        tokens = set(tokenize(sentence))
        if not tokens:
            continue
        score = len(tokens & keywords) / max(1.0, math.sqrt(len(tokens)))
        if score > best_score:
            best_score = score
            best = sentence
    return best[:max_chars]


def cosine_similarity(a: str, b: str) -> float:
    """Cosine similarity over word frequencies (stdlib only)."""
    va = _vector(tokenize(a))
    vb = _vector(tokenize(b))
    if not va or not vb:
        return 0.0
    dot = sum(va.get(w, 0) * vb.get(w, 0) for w in set(va) | set(vb))
    na = math.sqrt(sum(v * v for v in va.values()))
    nb = math.sqrt(sum(v * v for v in vb.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _vector(tokens) -> dict:
    vec = {}
    for t in tokens:
        vec[t] = vec.get(t, 0) + 1
    return vec


def load_text(path) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))