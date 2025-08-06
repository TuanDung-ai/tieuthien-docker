# memory/memory_manager.py
import os
from .db_supabase import (
    get_memory as get_memory_cloud,
    save_memory as save_memory_cloud,
    delete_memory as delete_memory_cloud,
    delete_single_memory as delete_single_memory_cloud
)

# === LƯU GHI NHỚ ===
def save_memory(user_id, content, note_type="khac"):
    print(f"Lưu trực tiếp vào Supabase: User ID={user_id}, Content='{content}', Type='{note_type}'")
    save_memory_cloud(user_id, content, note_type)

# === LẤY GHI NHỚ ===
def get_memory(user_id):
    print("Lấy dữ liệu từ Supabase.")
    memories = get_memory_cloud(user_id)
    return memories

# === XOÁ TOÀN BỘ GHI NHỚ ===
def clear_memory(user_id):
    print("Xóa toàn bộ dữ liệu khỏi Supabase.")
    delete_memory_cloud(user_id)

# === XOÁ MỘT GHI NHỚ THEO ID ===
def delete_single_memory(user_id, note_id):
    print(f"Xóa ghi nhớ có ID {note_id} cho user {user_id} từ Supabase.")
    delete_single_memory_cloud(user_id, note_id)
