"""Entry point for the Automated Assignment Evaluation Agent demo.

Run from `/content/project` (or the repo root) with:

    python main.py

It wires together the multi-agent pipeline and prints a full evaluation report
for a bundled sample submission. Add your own rubric/submission via the
--submission flag if you want to evaluate custom text.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the project importable regardless of where main.py is launched from
# (works for `python main.py` and `python /content/project/main.py`).
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from config.config import settings  # noqa: E402
from agents.agent import Assignment, Submission  # noqa: E402
from src.app import build_default_assignment, render, run_pipeline  # noqa: E402
from src.utils import summarize  # noqa: E402


SAMPLE_SUBMISSION = (
    "My essay explores how a clear, organized structure supports an independent "
    "and novel contribution to multi-agent systems. I present a critical analysis "
    "built on concrete evidence and a well-argued methodology. My approach links "
    "technical accuracy with proper citation of key literature, demonstrating an "
    "insightful, authoritative evaluation of current research, while keeping the "
    "writing concise and readable throughout. I evaluate trade-offs and cite "
    "authoritative sources to ground every claim."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Automated Assignment Evaluation Agent (demo)",
    )
    parser.add_argument(
        "--submission",
        help="Path to a text file containing the student submission.",
        default=None,
    )
    parser.add_argument(
        "--student",
        help="Student name shown on the report.",
        default="Alex Morgan",
    )
    return parser


def load_submission_text(path: str | None) -> str:
    if not path:
        return SAMPLE_SUBMISSION
    return Path(path).read_text(encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()

    assignment: Assignment = build_default_assignment()
    submission = Submission(
        student_name=args.student,
        text=load_submission_text(args.submission),
    )

    print("=" * 70)
    print("AUTOMATED ASSIGNMENT EVALUATION AGENT")
    print("=" * 70)
    print("Runtime settings:", settings.describe())
    print("Encrypted files detected:", settings.secret_keys_loaded or "none")
    print()

    payload = run_pipeline(assignment, submission)

    print(summarize(payload))
    print()
    print(render(payload))

    return 0


if __name__ == "__main__":
    sys.exit(main())