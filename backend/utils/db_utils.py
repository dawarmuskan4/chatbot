# db_utils.py
import sqlite3

DB_PATH = "conversations.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    add_username_column()
    
def add_username_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN username TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists — safe to ignore on repeated runs
    conn.close()

def save_message(session_id: str, role: str, content: str, username: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content, username) VALUES (?, ?, ?, ?)",
        (session_id, role, content, username)
    )
    
    conn.commit()
    conn.close()

def get_full_history(session_id: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    history = [{"role": role, "content": content} for role, content in rows]
    return history

# db_utils.py — new function

def get_user_conversations(username: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT session_id, MIN(created_at) as started_at, content
        FROM messages
        WHERE username = ? AND role = 'user'
        GROUP BY session_id
        ORDER BY started_at DESC
    """, (username,))
    
    rows = cursor.fetchall()
    conn.close()
    
    conversations = [{"session_id": session_id,"started_at":started_at, "preview": preview} for session_id, started_at, preview in rows]
    return conversations

def session_belongs_to_user(session_id: str, username: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM messages WHERE session_id = ? AND username = ? LIMIT 1",
        (session_id, username)
    )
    row = cursor.fetchone()
    conn.close()
    return row is not None
    
if __name__ == "__main__":
    init_db()
    save_message("db_test", "user", "Hello there",)
    save_message("db_test", "assistant", "Hi! How can I help?")
    print(get_full_history("db_test"))
    add_username_column()