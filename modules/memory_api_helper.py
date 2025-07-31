import os
import json
import gspread
from datetime import datetime
import time

# === LOG ENVIRONMENT ===
print("=== ENVIRONMENT VARIABLES ===")
for k, v in os.environ.items():
    print(f"{k} = {v[:100]}...")
print("=============================")

# === GOOGLE SHEETS KẾT NỐI ===
credentials_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
if not credentials_str:
    raise RuntimeError("❌ GOOGLE_CREDENTIALS_JSON chưa được thiết lập!")

try:
    credentials_data = json.loads(credentials_str)
except json.JSONDecodeError:
    try:
        fixed_str = credentials_str.encode().decode("unicode_escape")
        credentials_data = json.loads(fixed_str)
    except Exception as e:
        raise RuntimeError(f"❌ Lỗi JSON trong GOOGLE_CREDENTIALS_JSON: {e}")

gc = gspread.service_account_from_dict(credentials_data)
SHEET_NAME = "memorysheet"
worksheet = gc.open(SHEET_NAME).sheet1

# === KHỞI TẠO TIÊU ĐỀ ===
def ensure_headers():
    try:
        values = worksheet.get_all_values()
        if not values:
            worksheet.append_row(["user_id", "content", "note_type", "time"])
    except Exception as e:
        print("⚠️ Lỗi kiểm tra tiêu đề:", e)

ensure_headers()

# === LẤY DỮ LIỆU AN TOÀN VỚI RETRY ===
def safe_get_records(retries=3, delay=1.5):
    for attempt in range(retries):
        try:
            values = worksheet.get_all_values()
            if len(values) < 2:
                return []
            headers = values[0]
            return [dict(zip(headers, row)) for row in values[1:] if len(row) == len(headers)]
        except Exception as e:
            print(f"⚠️ Lỗi get_records, lần {attempt+1}: {e}")
            time.sleep(delay)
    return []

# === GHI NHỚ ===
def save_memory(user_id, content, note_type="khác"):
    time_str = datetime.now().isoformat()
    try:
        worksheet.append_row([str(user_id), content, note_type, time_str])
    except Exception as e:
        print(f"⚠️ Lỗi ghi nhớ:", e)

# === LẤY GHI NHỚ ===
def get_memory(user_id, note_type=None):
    records = safe_get_records()
    user_notes = [r for r in records if str(r.get("user_id", "")) == str(user_id)]
    if note_type:
        user_notes = [r for r in user_notes if r.get("note_type", "khác") == note_type]
    return user_notes

# === TÌM GHI NHỚ ===
def search_memory(user_id, keyword):
    notes = get_memory(user_id)
    keyword_lower = keyword.lower()
    return [(i, note) for i, note in enumerate(notes)
            if keyword_lower in note.get("content", "").lower() or keyword_lower in note.get("note_type", "").lower()]

# === XÓA TOÀN BỘ ===
def clear_memory(user_id):
    try:
        all_rows = worksheet.get_all_values()
        indices_to_delete = [i for i, row in enumerate(all_rows[1:], start=2) if row and row[0] == str(user_id)]
        for i in reversed(indices_to_delete):
            worksheet.delete_rows(i)
        return bool(indices_to_delete)
    except Exception as e:
        print(f"⚠️ Lỗi xóa ghi nhớ:", e)
        return False

# === CẬP NHẬT GHI NHỚ GẦN NHẤT ===
def update_latest_memory_type(user_id, note_type):
    records = safe_get_records()
    user_notes = [r for r in records if str(r.get("user_id", "")) == str(user_id)]
    if not user_notes:
        return False
    latest = user_notes[-1]
    try:
        all_rows = worksheet.get_all_values()
        for i, row in enumerate(all_rows[1:], start=2):
            if row and len(row) >= 4 and row[0] == str(user_id) and row[1] == latest["content"]:
                worksheet.update_cell(i, 3, note_type)
                return True
    except Exception as e:
        print(f"⚠️ Lỗi cập nhật dạng ghi nhớ:", e)
    return False

# === LẤY GHI NHỚ GẦN NHẤT DẠNG TEXT ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    notes.sort(key=lambda x: x.get("time", ""), reverse=True)
    recent = notes[:limit]
    return "\n".join(f"- ({n.get('note_type', 'khác')}) {n.get('content', '')}" for n in recent)
