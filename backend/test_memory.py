# quick test in main.py or a scratch script
from graph import graph
import uuid

session_id = str(uuid.uuid4())

def ask(query):
    initial_state = {
        "user_query": query,
        "has_document": False,
        "document_path": None,
        "session_id": session_id,
        "conversation_history": [],  # will be overwritten by api.py normally; for this test, load manually
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
    from memory_utils import get_conversation_history, add_message_to_history
    initial_state["conversation_history"] = get_conversation_history(session_id)
    result = graph.invoke(initial_state)
    add_message_to_history(session_id, "user", query)
    add_message_to_history(session_id, "assistant", result["final_answer"])
    return result["final_answer"]

print(ask("My name is Muskan and I like hiking."))
print(ask("What's my name?"))
print(ask("What hobby did I mention?"))