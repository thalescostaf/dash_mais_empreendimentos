from supabase import create_client
from dotenv import load_dotenv
import os

# Carrega o arquivo .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

resp = supabase.auth.sign_in_with_password({
    "email": "usuario@teste.com",
    "password": "123456"
})

print(resp)
