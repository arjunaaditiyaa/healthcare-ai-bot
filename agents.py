import re
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
from rag import retrieve_medical_context

llm = Ollama(model="llama3.1")

class MedicalState(TypedDict):
    query: str
    masked_query: Optional[str]
    context: Optional[str]
    doctor_answer: Optional[str]
    final_answer: Optional[str]

def mask_phi(state):
    q = state["query"]
    q = re.sub(r'\b\d{10}\b', '[PHONE]', q)
    q = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', '[DATE]', q)
    state["masked_query"] = q
    return state

def rag_node(state):
    state["context"] = retrieve_medical_context(
        state["masked_query"]
    )
    return state

def doctor_node(state):
    prompt = f"""
You are a medical information assistant.
Do NOT diagnose.
Use only the provided context.

Context:
{state["context"]}

Question:
{state["masked_query"]}
"""
    state["doctor_answer"] = llm.invoke(prompt)
    return state

def verifier_node(state):
    prompt = f"""
Verify safety.
Ensure:
- No diagnosis
- Evidence-based
- Add disclaimer

Text:
{state["doctor_answer"]}
"""
    state["final_answer"] = llm.invoke(prompt)
    return state

graph = StateGraph(MedicalState)

graph.add_node("mask", mask_phi)
graph.add_node("rag", rag_node)
graph.add_node("doctor", doctor_node)
graph.add_node("verifier", verifier_node)

graph.set_entry_point("mask")
graph.add_edge("mask", "rag")
graph.add_edge("rag", "doctor")
graph.add_edge("doctor", "verifier")
graph.add_edge("verifier", END)

medical_agent = graph.compile()
