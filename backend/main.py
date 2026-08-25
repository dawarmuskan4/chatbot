# main.py
from graph import graph

initial_state = {
    "user_query": "Who owns the frontend redesign, and what risk did the team flag?",
    "has_document": True,
    "document_path": "project_notes.docx",
    "intent": None,
    "df": None,
    "schema_context": None,
    "code": None,
    "previous_error": None,
    "validation_result": None,
    "retry_count": 0,
    "execution_result": None,
    "final_answer": None,
}

result = graph.invoke(initial_state)
print(result["final_answer"])