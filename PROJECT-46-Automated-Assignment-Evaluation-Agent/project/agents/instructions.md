# Agent Instructions

These are the operating instructions for the individual agents in the
evaluation pipeline. They are transferred to Colab and included in the project,
but the deterministic implementation lives in `agents/agent.py`.

## 1. Rubric Analysis Agent

- Validate that a rubric defines at least one criterion.
- Confirm the summed criterion points match the rubric total.
- Produce a structured analysis summary (criteria count, totals, balance).

## 2. Evaluation Agent

- Score every criterion against the matching rubric keywords.
- Ground each score in evidence extracted from the submission.
- Assign a score up to the criterion `max_points`.
- Add a small depth bonus for longer, more developed submissions.

## 3. Originality Agent

- Compare the submission against the bundled reference corpus.
- Report a cosine-similarity figure and a qualitative status:
  - `< 20%`  → HIGH ORIGINALITY
  - `< 45%`  → MODERATE SIMILARITY
  - `< 70%`  → ELEVATED SIMILARITY
  - `>= 70%` → POTENTIAL COPY REPLICATION

## 4. Feedback Agent

- Synthesize strengths and concrete improvements from per-criterion ratios.
- Provide actionable next steps for the student.
- Produce an executive summary with the overall percentage.

## Security note

`.enc` files are transferred **as-is** by the automation — they are never
decrypted and never opened. The configuration loader only attempts a best-effort
base64->JSON decode for runtime settings and safely falls back to defaults.