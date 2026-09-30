# 🎓 AutoEval AI — Automated Assignment Evaluation SaaS Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_RAG-FF6F00.svg)](https://www.trychroma.com/)
[![Tests](https://img.shields.io/badge/Pytest-11%20Passed%20100%25-brightgreen.svg)](https://docs.pytest.org/)

**AutoEval AI** is a production-grade, full-stack Agentic AI SaaS platform that revolutionizes educational assessment. It combines multi-agent orchestration, RAG-grounded retrieval, programmatic deterministic scoring, similarity analysis, and personalized feedback synthesis with a human-in-the-loop teacher review workflow.

---

## 🌟 Key Features

1. **Multi-Agent Evaluation Pipeline**:
   - `RubricAnalysisAgent`: Parses grading guidelines, enforces mathematical point allocations.
   - `EvaluationAgent`: Grounded criterion-by-criterion assessment using RAG context.
   - `ScoringAgent`: Programmatically computes exact total score without random LLM hallucination.
   - `FeedbackAgent`: Synthesizes actionable strengths, weaknesses, and concrete growth recommendations.
   - `EvaluationOrchestrator`: Coordinates all 8 stages and records audit trail into `AgentDecisionLog`.

2. **Document Processing & Extraction**:
   - Supports **PDF**, **DOCX**, and **Plain Text / Code** files (`.py`, `.java`, `.cpp`, etc.).
   - Extracts character and word counts with whitespace normalization.

3. **ChromaDB Vector Retrieval (RAG)**:
   - Indexes assignment briefs, solution guidelines, and course references.
   - Embeds context with `all-MiniLM-L6-v2` for semantic grounding.

4. **Originality & Similarity Checking**:
   - TF-IDF and n-gram cosine similarity comparing submissions against peer submissions and course materials.
   - Displays risk level (Low, Moderate, High), matching snippets, and explicit non-punitive AI disclaimer.

5. **Human-in-the-Loop Review & Publishing**:
   - AI evaluations are never published automatically.
   - Teachers can adjust criterion scores, edit qualitative feedback, add notes, and approve publication in 1 click with celebratory confetti.

6. **Role-Based Authentication & SaaS Portals**:
   - **Instructor Portal**: Dashboard analytics, Assignment wizard with rubric templates, Submissions pool, Evaluation detail inspector, and Published grades CSV export.
   - **Student Portal**: Dashboard KPIs, Assignment solution submission with instant word count, and comprehensive Graded Reports.
   - 1-Click Demo Login fast-switchers.

---

## 📐 Architecture & Workflow

```
                        ┌─────────────────────────────────────────┐
                        │           React 18 SaaS UI              │
                        │    (Instructor & Student Portals)       │
                        └────────────────────┬────────────────────┘
                                             │ HTTP REST / JWT
                                             ▼
                        ┌─────────────────────────────────────────┐
                        │          FastAPI Backend API            │
                        │      (Auth, CRUD, Orchestration)        │
                        └─────────┬───────────────────┬───────────┘
                                  │                   │
                     SQLAlchemy   │                   │ Extraction / Vector
                                  ▼                   ▼
    ┌───────────────────────────────┐       ┌─────────────────────────────────┐
    │     PostgreSQL / SQLite       │       │    Document Extractor & RAG     │
    │  (Users, Submissions, Grades) │       │   (pypdf, docx, ChromaDB)       │
    └───────────────────────────────┘       └────────────────┬────────────────┘
                                                             │
                                                             ▼
                                            ┌─────────────────────────────────┐
                                            │    Multi-Agent AI Pipeline      │
                                            │  ├─ 1. Document Extraction      │
                                            │  ├─ 2. Rubric Analysis Agent    │
                                            │  ├─ 3. Vector Context RAG       │
                                            │  ├─ 4. Criterion Evaluation     │
                                            │  ├─ 5. Originality Engine       │
                                            │  ├─ 6. Deterministic Scorer     │
                                            │  ├─ 7. Feedback Synthesis       │
                                            │  └─ 8. Teacher Review & Publish │
                                            └─────────────────────────────────┘
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- PostgreSQL (Optional, automatically falls back to local SQLite)

### 1. Backend Setup
```bash
# Navigate to backend and install dependencies
cd backend
pip install -r requirements.txt

# Run database migrations and seed demo data
cd ..
python run.py --seed

# The backend runs on http://localhost:8000
# OpenAPI Docs: http://localhost:8000/docs
```

### 2. Frontend Setup
```bash
# Navigate to frontend and start Vite dev server
cd frontend
npm install
npm run dev

# The frontend runs on http://localhost:5173
```

### 3. Demo Credentials (or use 1-Click buttons)
- **Teacher**: `teacher@evalagent.com` / `password123`
- **Student**: `student1@evalagent.com` / `password123`

### 4. Record a VS Code Walkthrough
From the repository root, install the screen-capture dependencies and run:
```bash
python -m pip install pyautogui mss opencv-python numpy
python whole_project_automation.py
```
This opens the repository in VS Code and creates `project_automation.mp4`.
Use `python whole_project_automation.py --dry-run` to validate the targets
without opening VS Code. For a shorter or longer capture, pass
`--seconds-per-file N`.

---

## 🧪 Automated Test Suite

Run the full backend test suite:
```bash
python backend/tests/run_tests.py
# or
pytest
```
```
backend/tests/test_auth.py::test_register_and_login_flow PASSED
backend/tests/test_auth.py::test_invalid_login_credentials PASSED
backend/tests/test_auth.py::test_role_authorization_guard PASSED
backend/tests/test_evaluation_pipeline.py::test_full_evaluation_and_teacher_approval_flow PASSED
backend/tests/test_extractor.py::test_plaintext_extraction PASSED
backend/tests/test_extractor.py::test_empty_document_raises_extraction_exception PASSED
backend/tests/test_rag_and_originality.py::test_text_chunker PASSED
backend/tests/test_rag_and_originality.py::test_originality_service_similarity PASSED
backend/tests/test_scoring.py::test_calculate_letter_grades PASSED
backend/tests/test_scoring.py::test_deterministic_scoring_enforces_bounds_and_exact_sum PASSED
backend/tests/test_scoring.py::test_deterministic_scoring_clips_overflown_and_negative_scores PASSED
====================== 11 passed in 47.80s =======================
```

---

## 🐳 Docker Deployment

To launch the full stack (PostgreSQL + FastAPI + Vite React) in containers:
```bash
docker-compose up --build
```
- App UI: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 📄 License
MIT License. Built for enterprise and educational institutions.
