import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

# === ĐỌC GOOGLE CREDENTIAL TỪ ENV BIẾN ===
creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
if creds_json is None:
    raise Exception("❗ Thiếu biến GOOGLE_CREDENTIALS_JSON – kiểm tra Zeabur.")

creds_data = json.loads(creds_json)

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_NAME = "MemorySheet"  # Đúng tên sheet bạn đã tạo

creds = Credentials.from_service_account_info(creds_data, scopes=SCOPE)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1

# === GHI NHỚ ===
def save_memory(user_id, content, note_type="khác"):
    time_str = datetime.now().isoformat()
    row = [str(user_id), content, note_type, time_str]
    sheet.append_row(row)

# === LẤY GHI NHỚ ===
def get_memory(user_id, note_type=None):
    all_data = sheet.get_all_values()
    result = []
    for row in all_data[1:]:  # bỏ dòng tiêu đề
        uid, content, ntype, time_str = row
        if uid == str(user_id):
            if note_type is None or note_type == ntype:
                result.append({
                    "content": content,
                    "type": ntype,
                    "time": time_str
                })
    return result

# === TÌM KIẾM ===
def search_memory(user_id, keyword):
    keyword = keyword.lower()
    notes = get_memory(user_id)
    result = []
    for idx, note in enumerate(notes):
        if keyword in note["content"].lower() or keyword in note["type"].lower():
            result.append((idx, note))
    return result

# === XÓA TOÀN BỘ GHI NHỚ USER ===
def clear_memory(user_id):
    all_data = sheet.get_all_values()
    indexes_to_delete = []
    for idx, row in enumerate(all_data[1:], start=2):
        if row[0] == str(user_id):
            indexes_to_delete.append(idx)
    for idx in reversed(indexes_to_delete):
        sheet.delete_rows(idx)
    return len(indexes_to_delete) > 0

# === CẬP NHẬT LOẠI CHO GHI NHỚ MỚI NHẤT ===
def update_latest_memory_type(user_id, note_type):
    all_data = sheet.get_all_values()
    latest_idx = -1
    for idx, row in enumerate(reversed(all_data[1:]), start=1):
        if row[0] == str(user_id):
            latest_idx = len(all_data) - idx
            break
    if latest_idx != -1:
        sheet.update_cell(latest_idx + 1, 3, note_type)
        return True
    return False

# === LẤY GHI NHỚ GẦN NHẤT ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    notes.sort(key=lambda x: x["time"], reverse=True)
    recent = notes[:limit]
    return "\n".join(f"- ({n['type']}) {n['content']}" for n in recent)
