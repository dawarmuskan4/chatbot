from utils.memory_utils import add_message_to_history, get_conversation_history
from fastapi import FastAPI, UploadFile, Form,HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import shutil
import os
from graph import graph
from fastapi.middleware.cors import CORSMiddleware
from utils.db_utils import save_message, init_db, get_full_history, get_user_conversations
from utils.auth_utils import create_user, authenticate_user, create_token, decode_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

init_db()


security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    username = decode_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username

@app.post("/ask-llm")
def query_endpoint(
    user_query: str = Form(...),
    session_id: str = Form(...),
    file: Optional[UploadFile] = None,
    username: str = Depends(get_current_user)
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
        "session_id": session_id,
        "conversation_history": history,
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
    
    ## saving to redis
    add_message_to_history(session_id, "user", user_query)
    add_message_to_history(session_id, "assistant", result["final_answer"])
    
    ## saving to db
    save_message(session_id, "user", user_query, username)
    save_message(session_id, "assistant", result["final_answer"], username)
    
    return {"answer": result["final_answer"]}

@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    success = create_user(username, password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already taken")
    token = create_token(username)
    return {"token": token}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    valid = authenticate_user(username, password)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(username)
    return {"token": token}

@app.get("/conversations")
def list_conversations(username: str = Depends(get_current_user)):
    return get_user_conversations(username)

@app.get("/conversations/{session_id}/messages")
def get_conversation_messages(session_id: str, username: str = Depends(get_current_user)):
    return get_full_history(session_id)