# memory/db_supabase.py
import os
from supabase import create_client, Client
import sys # Import sys for stderr

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "memories"

def get_supabase_client() -> Client:
    """Tạo và trả về client kết nối Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("LỖI SUPABASE: SUPABASE_URL hoặc SUPABASE_KEY không được thiết lập!", file=sys.stderr)
        raise ValueError("Supabase credentials are not set.")

    print(f"DEBUG: Supabase URL: {SUPABASE_URL[:20]}... (truncated)", file=sys.stderr) # Debug print
    print(f"DEBUG: Supabase Key: {SUPABASE_KEY[:5]}... (truncated)", file=sys.stderr) # Debug print
    
    try:
        # Cố gắng khởi tạo client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except TypeError as e:
        # Bắt lỗi TypeError cụ thể cho 'proxy' argument
        if "'proxy'" in str(e):
            print(f"LỖI SUPABASE: Lỗi 'proxy' khi khởi tạo client. Có thể do xung đột phiên bản hoặc cấu hình proxy tự động. Lỗi gốc: {e}", file=sys.stderr)
            print("Gợi ý: Đảm bảo không có biến môi trường HTTP_PROXY/HTTPS_PROXY nào đang gây ra vấn đề, hoặc thử hạ cấp/nâng cấp httpx/supabase.", file=sys.stderr)
        raise e # Re-raise the exception after printing debug info
    except Exception as e:
        print(f"LỖI SUPABASE: Lỗi không xác định khi khởi tạo client Supabase: {e}", file=sys.stderr)
        raise e # Re-raise for further investigation

def save_memory(user_id, content, note_type=None):
    """Lưu một ghi nhớ mới vào Supabase."""
    try:
        supabase = get_supabase_client()
        payload = {
            "user_id": user_id,
            "content": content,
            "note_type": note_type
        }
        print(f"DEBUG: Đang cố gắng lưu vào Supabase: {payload}", file=sys.stderr) # Debug print
        response = supabase.table(TABLE_NAME).insert(payload).execute()
        print(f"DEBUG: Supabase save response: {response.data}", file=sys.stderr) # Debug print
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu vào Supabase: {e}", file=sys.stderr)

def get_memory(user_id, note_type=None):
    """Lấy các ghi nhớ từ Supabase dựa trên user_id và note_type."""
    try:
        supabase = get_supabase_client()
        query = supabase.table(TABLE_NAME).select("*").eq("user_id", user_id)
        
        if note_type:
            query = query.eq("note_type", note_type)
            
        res = query.execute()
        print(f"DEBUG: Supabase get response: {res.data}", file=sys.stderr) # Debug print
        return res.data
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ Supabase: {e}", file=sys.stderr)
        return []

def delete_memory(user_id):
    """Xóa tất cả các ghi nhớ của một user_id trên Supabase."""
    try:
        supabase = get_supabase_client()
        print(f"DEBUG: Đang cố gắng xóa dữ liệu Supabase cho user: {user_id}", file=sys.stderr) # Debug print
        response = supabase.table(TABLE_NAME).delete().eq("user_id", user_id).execute()
        print(f"DEBUG: Supabase delete response: {response.data}", file=sys.stderr) # Debug print
    except Exception as e:
        print(f"Lỗi khi xóa dữ liệu trên Supabase: {e}", file=sys.stderr)

def get_all_cloud_memories():
    """Lấy tất cả các ghi nhớ từ Supabase."""
    try:
        supabase = get_supabase_client()
        print("DEBUG: Đang cố gắng lấy tất cả dữ liệu từ Supabase...", file=sys.stderr) # Debug print
        res = supabase.table(TABLE_NAME).select("*").execute()
        print(f"DEBUG: Supabase get all response: {res.data}", file=sys.stderr) # Debug print
        return res.data
    except Exception as e:
        print(f"Lỗi khi lấy tất cả dữ liệu từ Supabase: {e}", file=sys.stderr)
        return []
