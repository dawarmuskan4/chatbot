## Graphstate TypedDict

from os import strerror
from typing import TypedDict, Optional 

class GraphState(TypedDict):
    user_query: str 
    has_document: bool
    document_path: str
    intent: Optional[str]
    df: Optional[str]
    schema_context: Optional[str]
    code: Optional[str]
    execution_result: Optional[object]
    final_answer: Optional[str]
    previous_error: Optional[str]
    validation_result: Optional[str]
    retry_count: int
    session_id: Optional[str]
    conversation_history: Optional[list]
    