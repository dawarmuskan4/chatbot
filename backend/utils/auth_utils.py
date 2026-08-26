# auth_utils.py
import sqlite3
import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = "conversations.db"
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def init_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # same CREATE TABLE pattern as messages — this time: id, username (must be
    # unique — look up SQLite's UNIQUE constraint), password_hash, created_at
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    hashed = hash_password(password)
    
    try:
        # INSERT into users — same ? placeholder pattern as save_message.
        # username is UNIQUE, so what happens if someone tries to sign up
        # with a name that's already taken? Think about what SQLite will do,
        # and why this needs a try/except around it.
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def authenticate_user(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return False
    
    stored_hash = row[0]
    authenticated = verify_password(password, stored_hash)
    return authenticated  # you already have the right function for this

def create_token(username: str) -> str:
    payload ={
        "username": username,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token:str) -> str | None:
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["username"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


if __name__ == "__main__":
    token = create_token("muskan")
    print(token)
    print(decode_token(token))
    print(decode_token("garbage_not_a_real_token"))