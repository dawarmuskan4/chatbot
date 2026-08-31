# auth_utils.py
import sqlite3
import bcrypt
import jwt
import datetime
import os
import random
import resend
import datetime
from dotenv import load_dotenv
load_dotenv()

DB_PATH = "conversations.db"
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"
resend.api_key = os.environ.get("RESEND_API_KEY")

def init_users_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
  
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
    add_verification_columns()
    
def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_user_with_verification(username: str, password: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    hashed = hash_password(password)
    code = generate_verification_code()
    expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, verified, verification_code, code_expires_at) VALUES (?, ?, 0, ?, ?)",
            (username, hashed, code, expires_at)
        )
        conn.commit()
        conn.close()
        send_verification_email(username, code)
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

def add_verification_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for statement in [
        "ALTER TABLE users ADD COLUMN verified INTEGER DEFAULT 0",
        "ALTER TABLE users ADD COLUMN verification_code TEXT",
        "ALTER TABLE users ADD COLUMN code_expires_at TIMESTAMP",
    ]:
        try:
            cursor.execute(statement)
        except sqlite3.OperationalError:
            pass  # column already exists
    conn.commit()
    conn.close()

def generate_verification_code() -> str:
    code = random.randint(100000, 999999)
    return str(code)

def send_verification_email(to_email: str, code: str):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to_email,
        "subject": "Verify your account",
        "html": f"<p>Your verification code is: <strong>{code}</strong></p><p>It expires in 15 minutes.</p>",
    })
    
def verify_code(username: str, code: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT verification_code, code_expires_at FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return False

    stored_code, expires_at = row
    expires_at_dt = datetime.datetime.fromisoformat(expires_at)

    if code != stored_code or datetime.datetime.now(datetime.UTC) > expires_at_dt:
        conn.close()
        return False

    cursor.execute("UPDATE users SET verified = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return True

def is_verified(username: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT verified FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row is not None and row[0] == 1

if __name__ == "__main__":
    init_users_table()
    print(create_user_with_verification("dawarmuskan4@gmail.com", "testpass123"))