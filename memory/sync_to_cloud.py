# memory/sync_to_cloud.py
from .db_sqlite import get_all_local_memories
from .db_supabase import save_memory as save_memory_cloud
from .memory_storage import get_all_memories_storage

def sync_sqlite_to_supabase():
    """
    Đồng bộ dữ liệu từ SQLite (cache) lên Supabase (chính).
    Chỉ nên chạy khi bot khởi động để đảm bảo tính nhất quán.
    """
    print("🔄 Bắt đầu đồng bộ dữ liệu từ SQLite lên Supabase...")
    
    # Lấy tất cả dữ liệu từ SQLite
    local_memories = get_all_local_memories()
    
    if local_memories:
        for mem in local_memories:
            try:
                # Ghi dữ liệu lên Supabase. Supabase sẽ tự xử lý nếu dữ liệu đã tồn tại
                save_memory_cloud(mem['user_id'], mem['content'], mem['note_type'])
            except KeyError as e:
                print(f"Lỗi KeyError khi đồng bộ lên Supabase: {e}. Bỏ qua dòng này.")
        print(f"✅ Đã đồng bộ thành công {len(local_memories)} ghi nhớ lên Supabase.")
    else:
        print("⚠️ Không có dữ liệu để đồng bộ từ SQLite.")
