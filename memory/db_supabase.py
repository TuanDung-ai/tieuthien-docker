from supabase import create_client
import os

# Lấy biến môi trường Zeabur (không dùng .env)
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch toàn bộ bảng du_an
def fetch_du_an_supabase():
    res = supabase.table("du_an").select("*").execute()
    return res.data

# Insert 1 dự án vào Supabase
def insert_du_an_supabase(data_dict):
    supabase.table("du_an").insert(data_dict).execute()
