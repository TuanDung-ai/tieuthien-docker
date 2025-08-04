# memory/db_supabase.py
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "memories"

def get_supabase_client() -> Client:
    """Tạo và trả về client kết nối Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def save_memory(user_id, content, note_type=None):
    """Lưu một ghi nhớ mới vào Supabase."""
    try:
        supabase = get_supabase_client()
        payload = {
            "user_id": user_id,
            "content": content,
            "note_type": note_type
        }
        supabase.table(TABLE_NAME).insert(payload).execute()
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu vào Supabase: {e}")

def get_memory(user_id, note_type=None):
    """Lấy các ghi nhớ từ Supabase dựa trên user_id và note_type."""
    try:
        supabase = get_supabase_client()
        query = supabase.table(TABLE_NAME).select("*").eq("user_id", user_id)
        
        if note_type:
            query = query.eq("note_type", note_type)
            
        res = query.execute()
        return res.data
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ Supabase: {e}")
        return []

def delete_memory(user_id):
    """Xóa tất cả các ghi nhớ của một user_id trên Supabase."""
    try:
        supabase = get_supabase_client()
        supabase.table(TABLE_NAME).delete().eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Lỗi khi xóa dữ liệu trên Supabase: {e}")

def get_all_cloud_memories():
    """Lấy tất cả các ghi nhớ từ Supabase."""
    try:
        supabase = get_supabase_client()
        res = supabase.table(TABLE_NAME).select("*").execute()
        return res.data
    except Exception as e:
        print(f"Lỗi khi lấy tất cả dữ liệu từ Supabase: {e}")
        return []
