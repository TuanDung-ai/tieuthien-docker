import json
import os
from datetime import datetime

MEMORY_FILE = "memory.json"

def save_memory(user_id, content):
    data = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

    user_key = str(user_id)
    if user_key not in data:
        data[user_key] = []

    memory_item = {
        "content": content,
        "time": datetime.now().isoformat()
    }

    data[user_key].append(memory_item)

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_memory(user_id):
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    return data.get(str(user_id), [])
