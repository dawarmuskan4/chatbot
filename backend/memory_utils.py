# memory_utils.py
import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

MAX_TURNS = 12       # 6 exchanges = 12 messages (user+assistant pairs)
EXPIRY_SECONDS = 3600  # 1 hour

def add_message_to_history(session_id: str, role: str, content: str):
    key = f"conversation:{session_id}"
    history = get_conversation_history(session_id)
    
    history.append({"role": role, "content": content})
    history = history[-MAX_TURNS:]
    
    r.set(key, json.dumps(history), ex=EXPIRY_SECONDS)

def get_conversation_history(session_id: str) -> list[dict]:
    key = f"conversation:{session_id}"
    raw = r.get(key)
    if raw is None:
        return []
    history = json.loads(raw)
    return history