# memory/memory_manager.py
from .db_sqlite import get_memory as get_memory_local, save_memory as save_memory_local
from .db_supabase import get_memory as get_memory_cloud, save_memory as save_memory_cloud

def get_memory(user_id, note_type=None):
    """
    Lấy dữ liệu từ bộ nhớ. Ưu tiên lấy từ cache (SQLite).
    Nếu không có, lấy từ Supabase và ghi lại vào cache.
    """
    # Bước 1: Ưu tiên đọc từ SQLite cache
    local_data = get_memory_local(user_id, note_type)
    if local_data:
        print("Lấy dữ liệu từ SQLite (cache).")
        return local_data
    
    # Bước 2: Nếu cache trống, lấy từ Supabase
    print("SQLite trống, lấy dữ liệu từ Supabase.")
    cloud_data = get_memory_cloud(user_id, note_type)
    
    # Bước 3: Nếu có dữ liệu từ Supabase, ghi lại vào SQLite
    if cloud_data:
        print("Lấy dữ liệu từ Supabase và ghi lại vào SQLite.")
        for row in cloud_data:
            # Giả định dữ liệu trả về là một list dictionary
            save_memory_local(row['user_id'], row['content'], row['note_type'])
    
    return cloud_data

def save_memory(user_id, content, note_type=None):
    """
    Lưu dữ liệu vào cả SQLite và Supabase.
    """
    print("Lưu dữ liệu vào cả SQLite và Supabase.")
    # Ghi vào SQLite trước để có dữ liệu nhanh nhất
    save_memory_local(user_id, content, note_type)
    
    # Sau đó ghi vào Supabase
    save_memory_cloud(user_id, content, note_type)

def delete_memory(user_id):
    """
    Xóa dữ liệu khỏi cả SQLite và Supabase.
    """
    print("Xóa dữ liệu khỏi cả SQLite và Supabase.")
    # Xóa từ SQLite
    delete_memory_local(user_id)
    # Xóa từ Supabase
    delete_memory_cloud(user_id)

def get_all_memories():
    """
    Lấy tất cả dữ liệu từ Supabase, ghi vào SQLite và trả về.
    """
    print("Lấy tất cả dữ liệu từ Supabase và ghi lại vào SQLite.")
    cloud_data = get_all_cloud_memories()
    if cloud_data:
        for row in cloud_data:
            save_memory_local(row['user_id'], row['content'], row['note_type'])
    return cloud_data
