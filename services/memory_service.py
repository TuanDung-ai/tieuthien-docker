# services/memory_service.py

from modules.memory_manager import (
    save_memory as save_to_cloud,
    get_memory as get_from_cloud,
    delete_single_memory as delete_one,
    clear_memory as delete_all
)

def save_user_memory(user_id, content, note_type="khac"):
    return save_to_cloud(user_id, content, note_type)

def get_user_memories(user_id, note_type=None):
    return get_from_cloud(user_id, note_type)

def delete_user_memory(user_id, note_id):
    return delete_one(user_id, note_id)

def clear_user_memories(user_id):
    return delete_all(user_id)
