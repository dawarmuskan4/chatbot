# graph.py
from langgraph.graph import StateGraph, END
from state import GraphState
from utils.file_utils import get_file_type
from nodes import (
    classify_intent_node,
    generate_pandas_code_node,
    validate_code_node,
    execute_code_node,
    format_answer_node,
    failure_node,
    route_after_validation_node,
    load_document_node,
    load_text_document_node,
    text_qa_node,
)
from llm_client import ask_llm

def direct_answer_node(state: GraphState) -> dict:
    history = state["conversation_history"]
    
    history_text = "\n".join(f"{msg['role']}: {msg['content']}" for msg in history)
    
    user_content = f"Conversation so far:\n{history_text}\n\nNew question: {state['user_query']}"
    
    answer = ask_llm(user_content)
    return {"final_answer": answer}

def route_after_intent(state: GraphState) -> str:
    if state["intent"] == "direct":
        return "direct"
    return get_file_type(state["document_path"])

builder = StateGraph(GraphState)

builder.add_node("classify_intent", classify_intent_node)
builder.add_node("direct_answer", direct_answer_node)
builder.add_node("load_document", load_document_node)
builder.add_node("load_text_document", load_text_document_node)
builder.add_node("text_qa", text_qa_node)
builder.add_node("generate_pandas_code", generate_pandas_code_node)
builder.add_node("validate_code", validate_code_node)
builder.add_node("execute_code", execute_code_node)
builder.add_node("format_answer", format_answer_node)
builder.add_node("failure", failure_node)

builder.set_entry_point("classify_intent")

builder.add_conditional_edges(
    "classify_intent",
    route_after_intent,
    {
        "direct": "direct_answer",
        "tabular": "load_document",
        "text": "load_text_document",
    }
)

builder.add_edge("load_document", "generate_pandas_code")
builder.add_edge("generate_pandas_code", "validate_code")

builder.add_conditional_edges(
    "validate_code",
    route_after_validation_node,
    {
        "execute": "execute_code",
        "retry": "generate_pandas_code",
        "fail": "failure",
    }
)

builder.add_edge("execute_code", "format_answer")
builder.add_edge("load_text_document", "text_qa")

builder.add_edge("direct_answer", END)
builder.add_edge("format_answer", END)
builder.add_edge("failure", END)
builder.add_edge("text_qa", END)

graph = builder.compile()