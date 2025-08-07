from memory.db_supabase import (
    save_memory as save_to_cloud,
    get_memory as get_from_cloud,
    delete_single_memory as delete_one,
    delete_memory as delete_all
)

def save_memory(user_id, content, note_type="khac"):
    return save_to_cloud(user_id, content, note_type)

def get_memory(user_id, note_type=None):
    return get_from_cloud(user_id, note_type)

def delete_single_memory(user_id, note_id):
    return delete_one(user_id, note_id)

def clear_memory(user_id):
    return delete_all(user_id)
