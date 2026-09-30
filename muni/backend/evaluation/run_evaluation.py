"""Offline RAG evaluation harness (Ragas) + golden-set loader.

Usage (needs the runtime stack up):
    python evaluation/run_evaluation.py --datasets datasets/sample_qa.json

Metrics: faithfulness, answer_relevancy, context_precision, context_recall.
Results are printed as a table; exit code 1 if the mean faithfulness is
below --threshold (useful as a CI gate once the stack is reachable).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.schemas.query import QueryRequest  # noqa: E402
from app.services.query_service import QueryService  # noqa: E402


def load_dataset(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def collect_answers(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    service = QueryService(get_settings())
    rows: list[dict[str, Any]] = []
    for sample in samples:
        response = service.answer(QueryRequest(question=sample["question"], mode="basic"))
        rows.append({
            "question": response.question,
            "answer": response.answer,
            "contexts": [s.text for s in response.sources],
            "ground_truth": sample.get("ground_truth", ""),
        })
    return rows


def run_ragas(rows: list[dict[str, Any]]) -> dict[str, float]:
    from datasets import Dataset
    from ragas import evaluate
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    dataset = Dataset.from_list(rows)
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    return {k: float(v) for k, v in result.to_pandas().mean(numeric_only=True).items()
            if k in {"faithfulness", "answer_relevancy", "context_precision",
                     "context_recall"}}


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline RAG evaluation")
    parser.add_argument("--datasets", type=Path,
                        default=Path(__file__).parent / "datasets" / "sample_qa.json")
    parser.add_argument("--threshold", type=float, default=0.6,
                        help="Minimum mean faithfulness to pass")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    samples = load_dataset(args.datasets)
    print(f"Evaluating {len(samples)} samples from {args.datasets} …")

    rows = collect_answers(samples)
    try:
        scores = run_ragas(rows)
    except ImportError:
        print("ragas/datasets not installed — printing raw rows instead:\n")
        for row in rows:
            print(json.dumps(row, indent=2)[:600])
        return 0

    print("\n=== Ragas metrics ===")
    for metric, value in scores.items():
        print(f"{metric:>20}: {value:.3f}")
    if scores.get("faithfulness", 0.0) < args.threshold:
        print(f"\nFAIL: faithfulness below threshold {args.threshold}")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
