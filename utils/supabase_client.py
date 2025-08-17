import os
from supabase import create_client
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Variáveis SUPABASE_URL e SUPABASE_KEY não configuradas no .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Funções auxiliares
def get_table_data(table_name):
    res = supabase.table(table_name).select("*").execute()
    return res.data if res.data else []

def insert_data(table_name, data_dict):
    return supabase.table(table_name).insert(data_dict).execute().data

def update_data(table_name, row_id_name, row_id_value, data_dict):
    return supabase.table(table_name).update(data_dict).eq(row_id_name, row_id_value).execute().data

def delete_data(table_name, row_id_name, row_id_value):
    return supabase.table(table_name).delete().eq(row_id_name, row_id_value).execute().data
