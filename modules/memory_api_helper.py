import requests

# === Thay LINK API này bằng link thật trên Zeabur ===
API_BASE = "https://memory-thienco.zeabur.app"

# === ĐỌC NHỚ (GET) ===
def fetch_memory_from_api(user_id, limit=3):
    try:
        url = f"{API_BASE}/memories?user_id={user_id}&limit={limit}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data.get("memories_text", "")
    except Exception as e:
        print(f"Lỗi khi đọc nhớ từ API: {e}")
        return ""

# === GHI NHỚ (POST) ===
def save_memory_to_api(user_id, content, note_type="khác"):
    try:
        url = f"{API_BASE}/memories"
        payload = {
            "user_id": str(user_id),
            "content": content,
            "note_type": note_type
        }
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Lỗi khi ghi nhớ vào API: {e}")
        return False
