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
    
    # db_utils.py — add these two functions

def save_message(session_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # write an INSERT statement — think about SQL parameterization here,
    # NOT plain string formatting (f-strings). Look up sqlite3's "?" placeholder
    # syntax for cursor.execute() — this matters for security (SQL injection),
    # not just style
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
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
    
    # rows is a list of tuples like [("user", "hi"), ("assistant", "hello")]
    # convert it into the same shape you've used everywhere else tonight:
    # a list of {"role": ..., "content": ...} dicts
    history = [{"role": role, "content": content} for role, content in rows]
    return history
    
if __name__ == "__main__":
    init_db()
    save_message("db_test", "user", "Hello there")
    save_message("db_test", "assistant", "Hi! How can I help?")
    print(get_full_history("db_test"))