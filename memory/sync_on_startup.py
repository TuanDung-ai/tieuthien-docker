# memory/sync_on_startup.py
import sqlite3
from .db_supabase import get_all_cloud_memories
from .db_sqlite import save_memory, init_db

def ensure_sqlite_cache():
    """
    Đồng bộ dữ liệu từ Supabase về SQLite khi bot khởi động.
    """
    print("🔄 Bắt đầu đồng bộ dữ liệu từ Supabase về SQLite...")
    
    # Bước 1: Khởi tạo database SQLite để đảm bảo bảng tồn tại
    init_db()

    # Bước 2: Lấy tất cả dữ liệu từ Supabase
    cloud_memories = get_all_cloud_memories()

    # Bước 3: Ghi đè dữ liệu vào SQLite
    if cloud_memories:
        conn = sqlite3.connect("memory_full.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories") # Xóa dữ liệu cũ để đồng bộ
        conn.commit()
        conn.close()
        
        for mem in cloud_memories:
            try:
                save_memory(mem['user_id'], mem['content'], mem['note_type'])
            except KeyError as e:
                print(f"Lỗi KeyError khi lưu dữ liệu từ Supabase: {e}. Bỏ qua dòng này.")
        print(f"✅ Đã đồng bộ thành công {len(cloud_memories)} ghi nhớ.")
    else:
        print("⚠️ Không có dữ liệu để đồng bộ từ Supabase.")
