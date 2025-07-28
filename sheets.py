import os
import json
import time
import gspread
from datetime import datetime
from gspread.exceptions import APIError

print("=== ENVIRONMENT VARIABLES ===")
for k, v in os.environ.items():
    print(f"{k} = {v[:100]}...")
print("=============================")

# === KẾT NỐI GOOGLE SHEETS ===
credentials_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
if not credentials_str:
    raise RuntimeError("❌ Biến môi trường GOOGLE_CREDENTIALS_JSON chưa được thiết lập!")

try:
    credentials_data = json.loads(credentials_str)
except json.JSONDecodeError:
    try:
        fixed_str = credentials_str.encode().decode("unicode_escape")
        credentials_data = json.loads(fixed_str)
    except Exception as e:
        raise RuntimeError(f"❌ Lỗi JSON trong GOOGLE_CREDENTIALS_JSON: {e}")

# Tạo kết nối Google Sheets
gc = gspread.service_account_from_dict(credentials_data)
SHEET_NAME = "memorysheet"
worksheet = gc.open(SHEET_NAME).sheet1

# === GHI NHỚ ===
def save_memory(user_id, content, note_type="khác"):
    time_str = datetime.now().isoformat()
    worksheet.append_row([str(user_id), content, note_type, time_str])

# === LẤY GHI NHỚ ===
def get_memory(user_id, note_type=None, retries=3):
    for attempt in range(retries):
        try:
            records = worksheet.get_all_records()
            user_notes = [r for r in records if str(r.get("user_id", "")) == str(user_id)]
            if note_type:
                user_notes = [r for r in user_notes if r.get("type") == note_type]
            return user_notes
        except APIError as e:
            if '503' in str(e) and attempt < retries - 1:
                print(f"Google Sheets 503 – thử lại lần {attempt + 1}")
                time.sleep(1.5)
            else:
                print("Lỗi nghiêm trọng khi kết nối Sheets:", e)
                return []

# === TÌM KIẾM ===
def search_memory(user_id, keyword):
    notes = get_memory(user_id)
    keyword_lower = keyword.lower()
    return [(i, note) for i, note in enumerate(notes)
            if keyword_lower in note.get("content", "").lower() or keyword_lower in note.get("type", "").lower()]

# === XÓA TẤT CẢ GHI NHỚ ===
def clear_memory(user_id):
    all_rows = worksheet.get_all_values()
    indices_to_delete = [i for i, row in enumerate(all_rows[1:], start=2) if row[0] == str(user_id)]
    for i in reversed(indices_to_delete):
        worksheet.delete_rows(i)
    return bool(indices_to_delete)

# === XÓA 1 GHI NHỚ ===
def delete_memory_item(user_id, index):
    records = worksheet.get_all_records()
    user_notes = [r for r in records if str(r.get("user_id", "")) == str(user_id)]
    if 0 <= index < len(user_notes):
        target = user_notes[index]
        all_rows = worksheet.get_all_values()
        for i, row in enumerate(all_rows[1:], start=2):
            if (row[0] == str(user_id) and row[1] == target["content"]
                and row[2] == target["type"] and row[3] == target["time"]):
                worksheet.delete_rows(i)
                return True
    return False

# === CẬP NHẬT LOẠI GHI NHỚ GẦN NHẤT ===
def update_latest_memory_type(user_id, note_type):
    records = worksheet.get_all_records()
    user_notes = [r for r in records if str(r.get("user_id", "")) == str(user_id)]
    if not user_notes:
        return False
    latest = user_notes[-1]
    all_rows = worksheet.get_all_values()
    for i, row in enumerate(all_rows[1:], start=2):
        if (row[0] == str(user_id) and row[1] == latest["content"]
            and row[2] == latest["type"] and row[3] == latest["time"]):
            worksheet.update_cell(i, 3, note_type)
            return True
    return False

# === GHI NHỚ GẦN NHẤT CHO AI ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    notes.sort(key=lambda x: x.get("time", ""), reverse=True)
    recent = notes[:limit]
    return "\n".join(f"- ({n.get('type', 'khác')}) {n.get('content', '')}" for n in recent)
