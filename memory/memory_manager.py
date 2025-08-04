from .db_sqlite import (
    get_memory as get_memory_local,
    save_memory as save_memory_local,
    delete_memory as delete_memory_local,
    get_all_local_memories
)

from .db_supabase import (
    get_memory as get_memory_cloud,
    save_memory as save_memory_cloud,
    delete_memory as delete_memory_cloud,
    get_all_cloud_memories
)

# === LẤY DỮ LIỆU GHI NHỚ ===
def get_memory(user_id, note_type=None):
    """
    Lấy dữ liệu từ bộ nhớ. Ưu tiên lấy từ cache (SQLite).
    Nếu không có, lấy từ Supabase và ghi lại vào cache.
    """
    local_data = get_memory_local(user_id, note_type)
    if local_data:
        print("Lấy dữ liệu từ SQLite (cache).")
        return local_data

    print("SQLite trống, lấy dữ liệu từ Supabase.")
    cloud_data = get_memory_cloud(user_id, note_type)

    if cloud_data:
        print("Lấy dữ liệu từ Supabase và ghi lại vào SQLite.")
        for row in cloud_data:
            save_memory_local(row['user_id'], row['content'], row['note_type'])

    return cloud_data

# === LƯU GHI NHỚ ===
def save_memory(user_id, content, note_type=None):
    print("Lưu dữ liệu vào cả SQLite và Supabase.")
    save_memory_local(user_id, content, note_type)
    save_memory_cloud(user_id, content, note_type)

# === XOÁ GHI NHỚ ===
def delete_memory(user_id):
    print("Xóa dữ liệu khỏi cả SQLite và Supabase.")
    delete_memory_local(user_id)
    delete_memory_cloud(user_id)

# === ĐỒNG BỘ TOÀN BỘ GHI NHỚ ===
def get_all_memories():
    print("Lấy tất cả dữ liệu từ Supabase và ghi lại vào SQLite.")
    cloud_data = get_all_cloud_memories()
    if cloud_data:
        for row in cloud_data:
            save_memory_local(row['user_id'], row['content'], row['note_type'])
    return cloud_data

# === TÌM GHI NHỚ ===
def search_memory(user_id, keyword):
    notes = get_memory(user_id)
    keyword_lower = keyword.lower()
    return [(i, note) for i, note in enumerate(notes)
            if keyword_lower in note.get("content", "").lower() or keyword_lower in note.get("note_type", "").lower()]

# === XOÁ TOÀN BỘ GHI NHỚ ===
def clear_memory(user_id):
    delete_memory_local(user_id)
    delete_memory_cloud(user_id)
    print(f"✅ Đã xoá toàn bộ ghi nhớ cho user {user_id}")

# === LẤY GHI NHỚ GẦN NHẤT (CHO AI PROMPT) ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    recent = notes[:limit]
    return "\n".join(f"- ({n['note_type']}) {n['content']}" for n in recent)
