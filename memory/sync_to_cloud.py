from db_sqlite import get_all_local_memories
from db_supabase import get_all_cloud_memories, add_memory_cloud

def sync_sqlite_to_supabase():
    local = get_all_local_memories()
    cloud = get_all_cloud_memories()

    # Tạo set các ghi nhớ đã có trên Supabase để so sánh
    cloud_set = set((m['user_id'], m['content'], m['note_type'], m['time']) for m in cloud)

    added_count = 0
    for mem in local:
        key = (mem['user_id'], mem['content'], mem['note_type'], mem['time'])
        if key not in cloud_set:
            add_memory_cloud(mem['user_id'], mem['content'], mem['note_type'], mem['time'])
            added_count += 1

    print(f"✅ Đồng bộ SQLite → Supabase: đã thêm {added_count} bản ghi mới.")
