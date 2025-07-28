import os
import json
import gspread
from datetime import datetime

print("=== ENVIRONMENT VARIABLES ===")
for k, v in os.environ.items():
    print(f"{k} = {v[:100]}...")  # In 100 ký tự đầu tiên để tránh lộ khóa
print("=============================")

# === KẾT NỐI GOOGLE SHEETS ===
credentials_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
if not credentials_str:
    raise RuntimeError("❌ Biến môi trường GOOGLE_CREDENTIALS_JSON chưa được thiết lập!")

try:
    # Thử parse JSON trực tiếp
    credentials_data = json.loads(credentials_str)
except json.JSONDecodeError:
    try:
        # Nếu lỗi, thử giải mã escape (trường hợp Zeabur lưu escaped)
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
def get_memory(user_id, note_type=None):
    records = worksheet.get_all_records()
    user_notes = [r for r in records if str(r.get("user_id")) == str(user_id)]
    if note_type:
        user_notes = [r for r in user_notes if r.get("type") == note_type]
    return user_notes

# === TÌM KIẾM ===
def search_memory(user_id, keyword):
    notes = get_memory(user_id)
    keyword_lower = keyword.lower()
    return [(i, note) for i, note in enumerate(notes)
            if keyword_lower in note.get("content", "").lower() or keyword_lower in note.get("type", "").lower()]

# === XÓA TẤT CẢ GHI NHỚ CỦA USER ===
def clear_memory(user_id):
    all_rows = worksheet.get_all_values()
    indices_to_delete = [i for i, row in enumerate(all_rows[1:], start=2) if row[0] == str(user_id)]
    for i in reversed(indices_to_delete):
        worksheet.delete_rows(i)
    return bool(indices_to_delete)

# === XÓA MỘT GHI NHỚ THEO INDEX ===
def delete_memory_item(user_id, index):
    records = worksheet.get_all_records()
    user_notes = [r for r in records if str(r.get("user_id")) == str(user_id)]
    if 0 <= index < len(user_notes):
        target = user_notes[index]
        all_rows = worksheet.get_all_values()
        for i, row in enumerate(all_rows[1:], start=2):
            if (row[0] == str(user_id) and row[1] == target.get("content")
                and row[2] == target.get("type") and row[3] == target.get("time")):
                worksheet.delete_rows(i)
                return True
    return False

# === CẬP NHẬT LOẠI GHI NHỚ GẦN NHẤT ===
def update_latest_memory_type(user_id, note_type):
    records = worksheet.get_all_records()
    user_notes = [r for r in records if str(r.get("user_id")) == str(user_id)]
    if not user_notes:
        return False
    latest = user_notes[-1]
    all_rows = worksheet.get_all_values()
    for i, row in enumerate(all_rows[1:], start=2):
        if (row[0] == str(user_id) and row[1] == latest.get("content")
            and row[2] == latest.get("type") and row[3] == latest.get("time")):
            worksheet.update_cell(i, 3, note_type)
            return True
    return False

# === GHI NHỚ GẦN NHẤT (CHO PROMPT AI) ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    if not notes:
        return "Chưa có ghi nhớ nào."

    notes.sort(key=lambda x: x.get("time", ""), reverse=True)
    recent = notes[:limit]

    formatted = []
    for n in recent:
        try:
            formatted.append(f"- ({n['type']}) {n['content']}")
        except KeyError:
            print("⚠️ Ghi nhớ thiếu trường 'type' hoặc 'content':", n)
            continue
    return "\n".join(formatted) if formatted else "Chưa có ghi nhớ nào hợp lệ."
