# test_supabase.py
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

# a harmless call just to prove the client can authenticate
response = supabase.table("nonexistent_table_test").select("*").limit(1).execute()
print(response)