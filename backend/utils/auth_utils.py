# auth_utils.py
import os
import random
import datetime
import jwt
import bcrypt
import resend
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"

resend.api_key = os.environ.get("RESEND_API_KEY")


# ---- password hashing — unchanged, no DB involved ----

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# ---- JWT — unchanged, no DB involved ----

def create_token(username: str) -> str:
    payload = {
        "username": username,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["username"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ---- verification code + email — unchanged, no DB involved ----

def generate_verification_code() -> str:
    return str(random.randint(100000, 999999))


def send_verification_email(to_email: str, code: str):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": to_email,
        "subject": "Verify your account",
        "html": f"<p>Your verification code is: <strong>{code}</strong></p><p>It expires in 15 minutes.</p>",
    })


# ---- everything below is migrated from sqlite3 to Supabase ----

def create_user_with_verification(username: str, password: str) -> bool:
    hashed = hash_password(password)
    code = generate_verification_code()
    expires_at = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)).isoformat()

    try:
        supabase.table("chatbot_users").insert({
            "username": username,
            "password_hash": hashed,
            "verified": 0,
            "verification_code": code,
            "code_expires_at": expires_at,
        }).execute()
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return False
        raise  # something else went wrong — don't silently swallow it

    send_verification_email(username, code)
    return True


def authenticate_user(username: str, password: str) -> bool:
    response = (
        supabase.table("chatbot_users")
        .select("password_hash")
        .eq("username", username)
        .execute()
    )
    if not response.data:
        return False

    stored_hash = response.data[0]["password_hash"]
    return verify_password(password, stored_hash)


def verify_code(username: str, code: str) -> bool:
    response = (
        supabase.table("chatbot_users")
        .select("verification_code, code_expires_at")
        .eq("username", username)
        .execute()
    )
    if not response.data:
        return False

    row = response.data[0]
    stored_code = row["verification_code"]
    expires_at_dt = datetime.datetime.fromisoformat(row["code_expires_at"])

    if code != stored_code or datetime.datetime.now(datetime.UTC) > expires_at_dt:
        return False

    supabase.table("chatbot_users").update({"verified": 1}).eq("username", username).execute()
    return True


def is_verified(username: str) -> bool:
    response = (
        supabase.table("chatbot_users")
        .select("verified")
        .eq("username", username)
        .execute()
    )
    return bool(response.data) and response.data[0]["verified"] == 1


def resend_verification_code(username: str) -> bool:
    response = (
        supabase.table("chatbot_users")
        .select("verified")
        .eq("username", username)
        .execute()
    )
    if not response.data or response.data[0]["verified"] == 1:
        return False

    code = generate_verification_code()
    expires_at = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15)).isoformat()

    supabase.table("chatbot_users").update({
        "verification_code": code,
        "code_expires_at": expires_at,
    }).eq("username", username).execute()

    send_verification_email(username, code)
    return True


if __name__ == "__main__":
    print(create_user_with_verification("dawarmuskan4@gmail.com", "testpass123"))