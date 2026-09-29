import os
from datetime import datetime
from typing import TypedDict, Literal

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

load_dotenv(r"D:\Agent_Flow\.env", override=True)

if not os.getenv("OPENROUTER_API_KEY"):
    st.error("OPENROUTER_API_KEY was not found. Check D:\\Agent_Flow\\.env")
    st.stop()

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

@tool
def search_docs(query: str) -> str:
    """Search the internal knowledge base."""
    docs = {
        "langgraph": "LangGraph is a framework for building stateful, graph-based AI agent workflows.",
        "rag": "RAG retrieves relevant information and gives that context to an LLM before generating an answer.",
        "agent": "An AI agent combines a language model, tools, state, and workflow logic to complete tasks.",
        "memory": "LangGraph memory uses a checkpointer and thread ID to persist graph state."
    }
    q = query.lower()
    matches = [v for k, v in docs.items() if k in q]
    return "\n".join(matches) if matches else "No relevant documents found."

@tool
def calculator(expression: str) -> str:
    """Calculate an arithmetic expression."""
    allowed = set("0123456789+-*/(). ")
    if not expression or not set(expression).issubset(allowed):
        return "Invalid expression."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Calculation error: {e}"

class SupervisorState(TypedDict):
    query: str
    category: str
    research: str
    analysis: str
    response: str
    approved: bool
    history: list
    error: str
    retry_count: int

def classify_node(state):
    q = state["query"].lower()
    if any(w in q for w in ["calculate", "math", "plus", "minus", "multiply", "divide"]) or any(s in q for s in ["+", "*", "/"]):
        return {"category": "math"}
    if any(w in q for w in ["rag", "langgraph", "agent", "memory", "what is", "explain", "research"]):
        return {"category": "research"}
    return {"category": "general"}

def supervisor_router(state) -> Literal["math_node", "research_agent", "response_agent"]:
    return {
        "math": "math_node",
        "research": "research_agent",
        "general": "response_agent"
    }.get(state.get("category", "general"), "response_agent")

def math_node(state):
    try:
        prompt = f'Extract only the mathematical expression from: {state["query"]}. Return only the expression.'
        expression = llm.invoke(prompt).content.strip()
        return {"response": f"Calculation result: {calculator.invoke(expression)}", "error": ""}
    except Exception as e:
        return {"error": f"Math agent failed: {e}"}

def research_agent(state):
    try:
        context = search_docs.invoke(state["query"])
        prompt = f"""Answer the question using only this context.

Question:
{state["query"]}

Context:
{context}

Do not invent unsupported facts."""
        response = llm.invoke(prompt)
        return {"research": context, "response": response.content, "error": ""}
    except Exception as e:
        return {"error": f"Research agent failed: {e}"}

def response_agent(state):
    try:
        response = llm.invoke(state["query"])
        return {"response": response.content, "error": ""}
    except Exception as e:
        return {"error": f"Response agent failed: {e}"}

def analysis_agent(state):
    try:
        prompt = f"""Improve this proposed answer.

Question:
{state["query"]}

Research:
{state.get("research", "")}

Draft:
{state.get("response", "")}

Return only the final answer."""
        response = llm.invoke(prompt)
        return {"analysis": response.content, "response": response.content, "error": ""}
    except Exception as e:
        return {"error": f"Analysis agent failed: {e}"}

def approval_node(state):
    if state.get("error"):
        return {"approved": False}
    decision = interrupt({
        "question": "Approve the proposed response?",
        "query": state["query"],
        "response": state["response"]
    })
    return {"approved": decision == "approved"}

def route_after_approval(state):
    if state.get("error"):
        return "error_handler"
    return "end" if state.get("approved") else "retry_node"

def retry_node(state):
    return {
        "retry_count": state.get("retry_count", 0) + 1,
        "response": "The response was rejected by the human reviewer. Please review and submit again."
    }

def error_handler_node(state):
    return {
        "response": f"⚠️ Workflow failed.\n\nReason: {state.get('error', 'Unknown error')}"
    }

checkpointer = InMemorySaver()
graph = StateGraph(SupervisorState)

graph.add_node("classify", classify_node)
graph.add_node("math_node", math_node)
graph.add_node("research_agent", research_agent)
graph.add_node("analysis_agent", analysis_agent)
graph.add_node("response_agent", response_agent)
graph.add_node("approval", approval_node)
graph.add_node("retry_node", retry_node)
graph.add_node("error_handler", error_handler_node)

graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", supervisor_router, {
    "math_node": "math_node",
    "research_agent": "research_agent",
    "response_agent": "response_agent"
})
graph.add_edge("math_node", "approval")
graph.add_edge("research_agent", "analysis_agent")
graph.add_edge("analysis_agent", "approval")
graph.add_edge("response_agent", "approval")
graph.add_conditional_edges("approval", route_after_approval, {
    "end": END,
    "retry_node": "retry_node",
    "error_handler": "error_handler"
})
graph.add_edge("retry_node", END)
graph.add_edge("error_handler", END)

app = graph.compile(checkpointer=checkpointer)

st.set_page_config(page_title="LangGraph Agentic AI", page_icon="🤖", layout="centered")
st.title("🤖 LangGraph Agentic AI")
st.caption("OpenRouter + LangGraph + RAG + Memory + Human Approval")

thread_id = st.text_input("Thread ID", value="streamlit-session-1")
query = st.text_area("Enter your question", placeholder="Example: What is RAG? or Calculate 25 * 4")

if "pending" not in st.session_state:
    st.session_state.pending = None

if st.button("Run Agent", type="primary"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "query": query,
            "category": "",
            "research": "",
            "analysis": "",
            "response": "",
            "approved": False,
            "history": [],
            "error": "",
            "retry_count": 0
        }
        try:
            result = app.invoke(initial_state, config=config)
            st.session_state.pending = {"result": result, "config": config}
            st.rerun()
        except Exception as e:
            st.error(f"Workflow error: {e}")

pending = st.session_state.pending

if pending:
    result = pending["result"]
    config = pending["config"]

    if "__interrupt__" in result:
        data = result["__interrupt__"][0].value
        st.subheader("Human Approval Required")
        st.info(data.get("question", "Approve?"))
        st.write("**Query:**", data.get("query", ""))
        st.write("**Proposed response:**")
        st.write(data.get("response", ""))

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Approve"):
                try:
                    final = app.invoke(Command(resume="approved"), config=config)
                    st.success("Approved")
                    st.write(final.get("response", ""))
                    st.session_state.pending = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Resume error: {e}")

        with col2:
            if st.button("❌ Reject"):
                try:
                    final = app.invoke(Command(resume="rejected"), config=config)
                    st.warning("Rejected")
                    st.write(final.get("response", ""))
                    st.session_state.pending = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Resume error: {e}")

    else:
        st.subheader("Final Response")
        st.write(result.get("response", ""))
        st.session_state.pending = None

with st.expander("Current thread state"):
    try:
        state = app.get_state({"configurable": {"thread_id": thread_id}})
        st.json(dict(state.values))
    except Exception:
        pass
