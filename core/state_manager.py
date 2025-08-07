# core/state_manager.py
# Dùng nếu muốn lưu trạng thái tạm (như chờ nội dung ghi nhớ)

user_states = {}

def get_user_state(user_id):
    return user_states.get(user_id, {})

def set_user_state(user_id, state: dict):
    user_states[user_id] = state

def clear_user_state(user_id):
    user_states.pop(user_id, None)
