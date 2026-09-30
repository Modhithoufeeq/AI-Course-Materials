# Automated Assignment Evaluation Agent

A dependency-free, deterministic multi-agent evaluation pipeline. This is the
project transferred **as a whole** to Google Colab by
[`whole_project_automation.py`](../whole_project_automation.py), which
recursively discovers every supported file, recreates the exact folder
hierarchy under `/content/project`, and then runs the configured entry point
(`main.py`).

## Project layout

```text
project/
│
├── main.py            # Entry point (run by the automation after transfer)
├── README.md          # this file
├── requirements.txt   # minimal / dependency-free
├── .env.enc           # encrypted (base64) env settings — copied as-is
│
├── src/
│   ├── app.py         # wires the pipeline together
│   └── utils.py       # report formatting helpers
│
├── config/
│   ├── config.py      # runtime settings loader
│   └── settings.enc   # encrypted (base64) settings — copied as-is
│
└── agents/
    ├── agent.py       # multi-agent pipeline (rubric/eval/originality/feedback)
    ├── tools.py       # stdlib text-analysis utilities
    └── instructions.md
```

## What the automation does

1. Recursively discovers every `.py`, `.md` and `.enc` file under `project/`.
2. Validates all Python files (`ast.parse`) before starting.
3. Base64-encodes each file so its bytes are restored **exactly** in Colab.
   `.enc` files are copied verbatim — never decrypted.
4. Recreates the folder hierarchy under `/content/project` in Colab.
5. Runs the configurable entry point (`main.py`) from `/content/project`.
6. Records the entire flow to `project_automation.mp4`.

## Run locally

```bash
cd project
python main.py                     # sample essay submission
python main.py --student "Jordan Lee"   # custom student name
python main.py --submission essay.txt --student "Alex"  # custom text
```

## Quick test of the transfer

From the repository root (where `whole_project_automation.py` lives):

```bash
python whole_project_automation.py --dry-run
```

This discovers, validates, generates and then **re-executes** the exact Colab
transfer cell against a temp folder, proving every file is rebuilt byte-for-byte
— no browser or screen recording required.