"""CrewAI crew: researcher agent (retrieval tool) + synthesiser agent.

Runs only when ``AGENTIC_MODE`` is enabled (or ``mode=agentic`` requested).
CrewAI / langchain-ollama are imported lazily so the API can serve basic RAG
even when the agent stack is not installed.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field, PrivateAttr

from app.core.config import Settings
from app.core.rag.retriever import Retriever
from app.prompts.agents.system_prompts import (
    COORDINATOR_BACKSTORY,
    COORDINATOR_GOAL,
    COORDINATOR_ROLE,
    COORDINATOR_TASK,
    RESEARCHER_BACKSTORY,
    RESEARCHER_GOAL,
    RESEARCHER_ROLE,
    RESEARCHER_TASK,
)

logger = logging.getLogger(__name__)


class RetrievalToolInput(BaseModel):
    question: str = Field(description="The search question to run against the "
                                     "document knowledge base.")


def _build_tool(settings: Settings, retriever: Retriever) -> Any:
    from crewai.tools import BaseTool

    class _RetrievalTool(BaseTool):
        name: str = "knowledge_base_search"
        description: str = (
            "Search the company document knowledge base. Use this for any "
            "factual question about policies, reports, or stored documents."
        )
        args_schema: type[BaseModel] = RetrievalToolInput
        _retriever: Retriever = PrivateAttr(default=None)  # type: ignore[assignment]

        def _run(self, question: str) -> str:
            try:
                sources = self._retriever.retrieve(question)
            except Exception as exc:  # noqa: BLE001 — tools must not crash the crew
                return f"Search failed: {exc}"
            if not sources:
                return "No documents in the knowledge base matched the query."
            return "\n\n".join(
                f"[{s.index}] ({s.filename}, score={s.score}): {s.text}"
                for s in sources
            )

    tool = _RetrievalTool()
    tool._retriever = retriever
    return tool


def _build_retrieval_tool(settings: Settings, retriever: Retriever) -> Any:
    return _build_tool(settings, retriever)


class AgenticQueryOrchestrator:
    """Two-agent sequential crew over the shared vector retriever."""

    def __init__(self, settings: Settings, retriever: Retriever,
                 temperature: float | None = None) -> None:
        self.settings = settings
        self._retriever = retriever
        self._temperature = temperature

    def run(self, question: str) -> str:
        from crewai import Agent, Crew, Process, Task

        from app.core.rag.llm import get_langchain_llm

        llm = get_langchain_llm(self.settings, self._temperature)
        tool = _build_retrieval_tool(self.settings, self._retriever)

        researcher = Agent(
            role=RESEARCHER_ROLE,
            goal=RESEARCHER_GOAL,
            backstory=RESEARCHER_BACKSTORY,
            llm=llm,
            tools=[tool],
            allow_delegation=False,
            verbose=self.settings.CREW_VERBOSE,
        )
        coordinator = Agent(
            role=COORDINATOR_ROLE,
            goal=COORDINATOR_GOAL,
            backstory=COORDINATOR_BACKSTORY,
            llm=llm,
            allow_delegation=False,
            verbose=self.settings.CREW_VERBOSE,
        )

        search_task = Task(
            description=RESEARCHER_TASK.format(question=question),
            expected_output="The retrieved passages with their source file names.",
            agent=researcher,
        )
        synthesis_task = Task(
            description=COORDINATOR_TASK.format(question=question),
            expected_output=(
                "A concise, grounded answer with [filename] citations, or the "
                "exact 'not found' sentence."
            ),
            agent=coordinator,
            context=[search_task],
        )

        crew = Crew(
            agents=[researcher, coordinator],
            tasks=[search_task, synthesis_task],
            process=Process.sequential,
            verbose=self.settings.CREW_VERBOSE,
        )
        result = crew.kickoff(inputs={"question": question})
        answer = getattr(result, "raw", None) or str(result)
        logger.info("Agentic crew finished (%d chars)", len(answer))
        return answer.strip()
