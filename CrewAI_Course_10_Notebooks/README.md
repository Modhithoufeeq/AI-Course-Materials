# CrewAI Course - 10 Hands-On Notebooks

## Setup Instructions

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run notebooks in order:**
   - Start with `01_Introduction_to_CrewAI.ipynb`
   - Progress through `02` to `10`
   - Each notebook builds on the previous one

## Notebook Overview

| # | Notebook | What You Will Build |
|---|----------|---------------------|
| 01 | Introduction to CrewAI | Your first CrewAI app with 1 agent + 1 task |
| 02 | CrewAI Agents | 3 specialized agents (Researcher, Analyst, Writer) |
| 03 | Tasks in CrewAI | Multi-step workflow with task dependencies |
| 04 | Crews and Processes | Sequential vs Hierarchical crew comparison |
| 05 | Tools in CrewAI | Custom tools: calculator, file reader, API, lookup |
| 06 | Memory and Knowledge | Memory-enabled vs disabled crew comparison |
| 07 | CrewAI with RAG | Document research crew with FAISS vector DB |
| 08 | Multi-Agent Collaboration | Research -> Analysis -> Writing -> Review pipeline |
| 09 | CrewAI Flows | Event-driven workflows with conditional routing |
| 10 | Production CrewAI | End-to-end project with supervisor, RAG, tools, Streamlit UI |

## Prerequisites
- Python 3.10 or higher
- OpenAI API key (set in `.env` file)
- Jupyter Notebook or JupyterLab

## Video Recording Tips
Each notebook is structured for direct video recording:
- Markdown cells = theory/explanation (read aloud)
- Code cells = hands-on demo (run and explain)
- Output cells = show results
- Summary cells = recap what was learned

## Support
For issues, ensure:
1. `.env` file has a valid `OPENAI_API_KEY`
2. All dependencies are installed: `pip install -r requirements.txt`
3. Python version is 3.10+
