# memory/memory_manager.py
from .db_supabase import (
    get_memory as get_memory_cloud,
    save_memory as save_memory_cloud,
    delete_memory as delete_memory_cloud,
    get_all_cloud_memories
)

# === LẤY DỮ LIỆU GHI NHỚ ===
def get_memory(user_id, note_type=None):
    """
    Lấy dữ liệu trực tiếp từ Supabase.
    """
    print("Lấy dữ liệu từ Supabase.")
    return get_memory_cloud(user_id, note_type)

# === LƯU GHI NHỚ ===
def save_memory(user_id, content, note_type=None):
    """
    Lưu ghi nhớ trực tiếp vào Supabase.
    """
    print(f"Lưu trực tiếp vào Supabase: User ID={user_id}, Content='{content}', Type='{note_type}'")
    save_memory_cloud(user_id, content, note_type)

# === XOÁ GHI NHỚ ===
def delete_memory(user_id):
    """
    Xóa ghi nhớ trực tiếp trên Supabase.
    """
    print(f"Xóa dữ liệu trên Supabase cho user: {user_id}")
    delete_memory_cloud(user_id)

# === TÌM GHI NHỚ ===
def search_memory(user_id, keyword):
    """
    Lấy tất cả ghi nhớ từ Supabase và tìm kiếm cục bộ.
    """
    notes = get_memory_cloud(user_id)
    keyword_lower = keyword.lower()
    return [(i, note) for i, note in enumerate(notes)
            if keyword_lower in note.get("content", "").lower() or keyword_lower in note.get("note_type", "").lower()]

# === LẤY GHI NHỚ GẦN NHẤT (CHO AI PROMPT) ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    recent = notes[:limit]
    return "\n".join(f"- ({n['note_type']}) {n['content']}" for n in recent)

# === XOÁ TOÀN BỘ GHI NHỚ ===
def clear_memory(user_id):
    delete_memory(user_id)
    print(f"✅ Đã xoá toàn bộ ghi nhớ cho user {user_id}")
