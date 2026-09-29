# AI Agents & GenAI — Course Materials Collection

A consolidated collection of my **AI / Agentic-AI / GenAI learning projects**, notebooks,
course materials and hands-on demos — moved here from local zip archives so they are
version-controlled and viewable on the web.

---

## 📦 Projects in this repository

| # | Folder | What it is | Contents |
|---|--------|-----------|----------|
| 1 | [`Agent_Flow/`](./Agent_Flow) | **LangGraph agent workflows** — 11 progressive notebooks + a Streamlit app | `01_first_langgraph` → `10_end_to_end_agentic_ai`, multi-node workflows, routers, tool-calling, memory, human-in-the-loop, ReAct & supervisor multi-agent |
| 2 | [`CrewAI_Course_10_Notebooks/`](./CrewAI_Course_10_Notebooks) | **CrewAI course** — 10-module notebook series (+ OpenRouter variants) | Agents, tasks, crews & processes, tools, memory & knowledge, RAG, multi-agent collaboration, Flows, production |
| 3 | [`Complete-Agentic-AI-Course/`](./Complete-Agentic-AI-Course) | **Complete Agentic AI course** — LangChain ↔ LangGraph progression | `LangGraph-Code/` (13+ notebooks, HITL, subgraphs, guardrails, persistence), `LangChain-Multi-Agent-Research-System/`, `Langchain-Single-Agent/`, `Pydantic-Validation/`, async programming, interview-prep PDFs |
| 4 | [`Complete-GenAI-Course-Python-Langchain/`](./Complete-GenAI-Course-Python-Langchain) | **Complete GenAI course with Python & LangChain** | 19 notebooks (prompt chains → RAG → multi-agent) + 6 runnable Streamlit/CLI apps (QnA bot, Google agent, SQL agent, RAG agent, LangGraph bot) with sample data |
| 5 | [`agentic-ai-security/`](./agentic-ai-security) | **Agentic AI security** — secure vs. insecure agent comparison | `unsecure-ai-agent/` (prompt-injection-prone MCP agent) vs. `secure-ai-agent/` (hardened MCP server + guardrails), `pyproject.toml`, `uv.lock` |
| 6 | [`Class_Materials/`](./Class_Materials) | **Deep-learning class files** | ANN hyper-parameters, CNN, RNN/LSTM (+ machine-translation project), TensorFlow/Keras on MNIST, Word Embeddings (Word2Vec) — slides, PDFs, notebooks |

---

## 🔐 Environment variables (read this before running anything)

Every project expects a `.env` file that is **excluded from this repository on purpose**.
The variable *names* are preserved in the committed **`.env.example`** files.

To run a project:

```bash
cd <project-folder>
cp .env.example .env      # Windows: copy .env.example .env
# then open .env and paste in your own API keys
```

`.env.example` files are provided at:

- `Agent_Flow/.env.example`
- `CrewAI_Course_10_Notebooks/.env.example`
- `Complete-Agentic-AI-Course/LangGraph-Code/.env.example`
- `Complete-Agentic-AI-Course/LangGraph-Code/Agentic-Chatbot-using-LangGraph/.env.example`
- `Complete-Agentic-AI-Course/LangGraph-Code/Agentic-Chatbot-using-LangGraph/notebooks/.env.example`
- `Complete-GenAI-Course-Python-Langchain/.env.example`

Keys referenced across the projects: `OPENAI_API_KEY`, `OPENROUTER_API_KEY`,
`ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY`, `TAVILY_API_KEY`,
`SERPER_API_KEY`, `OPENWEATHER_API_KEY`, `HUGGINGFACEHUB_API_TOKEN`,
`LANGSMITH_API_KEY` / `LANGCHAIN_API_KEY`.

> ⚠️ **Never commit a real `.env`.** If a key ever gets pushed by accident, revoke it in
> the provider dashboard immediately — Git history is public and permanent.

---

## 🚀 Getting started

```bash
git clone https://github.com/Modhithoufeeq/<repo-name>.git
cd <repo-name>/<project-folder>

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
jupyter lab          # or: streamlit run app.py
```

Python virtual environments (`.venv*`), `__pycache__`, `node_modules` and OS junk are
git-ignored — recreate them locally after cloning.

---

## 📝 Notes

- This repository is a **consolidation of local course-material archives** (originally
  downloaded as `*-main.zip` bundles). Folder names were normalized and one duplicate
  archive (`CrewAI.zip` vs `CrewAI_Course_10_Notebooks.zip`) was merged.
- The ~386 MB Python virtualenv that shipped inside the original `CrewAI.zip` archive
  was intentionally **excluded** — it is reproducible from `requirements.txt` and would
  have exceeded GitHub's file-size limits.
- Course materials, PDFs and slide decks remain the property of their respective
  authors/instructors and are included here for personal study and reference.
