"""Report formatting helpers for the evaluation pipeline."""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any


def percentage_text(score: float, total: float) -> str:
    if not total:
        return "0.0%"
    return f"{score / total * 100:.1f}%"


def build_text_report(data: Dict[str, Any]) -> str:
    """Render the full evaluation result as a readable, self-contained report."""
    lines: List[str] = []
    width = 74
    sep = "=" * width

    lines.append(sep)
    lines.append(f"        AUTOMATED ASSIGNMENT EVALUATION REPORT")
    lines.append(sep)
    lines.append(f"Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Title     : {data['assignment_title']}")
    lines.append(f"Student   : {data['student_name']}")
    lines.append(f"Pipeline  : {data.get('pipeline', 'deterministic multi-agent')}")
    lines.append(sep)

    # Overall score block
    lines.append("OVERALL RESULT")
    lines.append("-" * width)
    total = data["total_score"]
    max_total = data["max_score"]
    lines.append(f"  Total score  : {total:.1f} / {max_total:.1f}")
    lines.append(f"  Percentage   : {percentage_text(total, max_total)}")
    grader = data.get("grade", "")
    if grader:
        lines.append(f"  Grade        : {grader}")
    lines.append("")

    # Criterion breakdown
    lines.append("CRITERION BREAKDOWN")
    lines.append("-" * width)
    for c in data.get("criteria", []):
        lines.append(f"  [+] {c['criterion']}  ({c['score']:.1f}/{c['max_points']:.1f} pts)")
        lines.append(f"      Evidence : \"{c['evidence']}\"")
        lines.append(f"      Strength : {c['strength']}")
        lines.append(f"      Improve  : {c['improvement']}")
        lines.append("")

    # Originality
    orig = data.get("originality", {})
    lines.append("ORIGINALITY")
    lines.append("-" * width)
    lines.append(f"  Similarity : {orig.get('similarity', 0.0):.1%}")
    lines.append(f"  Status     : {orig.get('status', 'n/a')}")
    lines.append("")

    # Feedback
    fb = data.get("feedback", {})
    lines.append("FEEDBACK / ACTION ITEMS")
    lines.append("-" * width)
    lines.append(f"  {fb.get('executive_summary', '')}")
    for item in fb.get("strengths", []):
        lines.append(f"  - STRENGTH  : {item}")
    for item in fb.get("improvements", []):
        lines.append(f"  - IMPROVE   : {item}")
    for item in fb.get("action_items", []):
        lines.append(f"  - ACTION    : {item}")
    lines.append("")
    lines.append(sep)

    return "\n".join(lines)


def grade_for(percentage: float) -> str:
    if percentage >= 0.90:
        return "A"
    if percentage >= 0.80:
        return "B"
    if percentage >= 0.70:
        return "C"
    if percentage >= 0.60:
        return "D"
    return "F"


def summarize(payload: Dict[str, Any]) -> str:
    total = payload["total_score"]
    max_total = payload["max_score"]
    pct = total / max_total if max_total else 0.0
    return (
        f"{payload['student_name']}: {total:.1f}/{max_total:.1f} "
        f"({percentage_text(total, max_total)}) grade {grade_for(pct)}"
    )