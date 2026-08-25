from memory_utils import add_message_to_history, get_conversation_history
from fastapi import FastAPI, UploadFile, Form
from typing import Optional
import shutil
import os
from graph import graph
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/ask-llm")
def query_endpoint(
    user_query: str = Form(...),
    session_id: str = Form(...),
    file: Optional[UploadFile] = None
):
    has_document = file is not None
    document_path = None
    
    if file:
        document_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(document_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    
    history = get_conversation_history(session_id)
    
    initial_state = {
        "user_query": user_query,
        "has_document": has_document,
        "document_path": document_path,
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
    
    add_message_to_history(session_id, "user", user_query)
    add_message_to_history(session_id, "assistant", result["final_answer"])
    
    return {"answer": result["final_answer"]}