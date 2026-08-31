# db_utils.py
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)


def init_db():
    # tables are already created via Supabase's SQL Editor — nothing to do here.
    # kept as a no-op so api.py's existing init_db() call doesn't need to change.
    pass


def save_message(session_id: str, role: str, content: str, username: str):
    supabase.table("chatbot_messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content,
        "username": username,
    }).execute()


def get_full_history(session_id: str) -> list[dict]:
    response = (
        supabase.table("chatbot_messages")
        .select("role, content")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )
    return response.data


def get_user_conversations(username: str) -> list[dict]:
    response = (
        supabase.table("chatbot_messages")
        .select("session_id, content, created_at")
        .eq("username", username)
        .eq("role", "user")
        .order("created_at")
        .execute()
    )

    seen = {}
    for row in response.data:
        sid = row["session_id"]
        if sid not in seen:
            seen[sid] = {
                "session_id": sid,
                "started_at": row["created_at"],
                "preview": row["content"],
            }

    conversations = list(seen.values())
    conversations.sort(key=lambda c: c["started_at"], reverse=True)
    return conversations


def session_belongs_to_user(session_id: str, username: str) -> bool:
    response = (
        supabase.table("chatbot_messages")
        .select("id")
        .eq("session_id", session_id)
        .eq("username", username)
        .limit(1)
        .execute()
    )
    return len(response.data) > 0


if __name__ == "__main__":
    save_message("db_test", "user", "Hello there", "test_user")
    save_message("db_test", "assistant", "Hi! How can I help?", "test_user")
    print(get_full_history("db_test"))
    print(get_user_conversations("test_user"))
    print(session_belongs_to_user("db_test", "test_user"))