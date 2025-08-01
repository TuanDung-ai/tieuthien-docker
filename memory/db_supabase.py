
from supabase import create_client
import os

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Truy vấn bảng du_an
def fetch_du_an():
    res = supabase.table("du_an").select("*").execute()
    return res.data

# Thêm bản ghi vào du_an
def insert_du_an(data_dict):
    supabase.table("du_an").insert(data_dict).execute()
