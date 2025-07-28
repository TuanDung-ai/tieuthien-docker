# sheets.py
import os
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# === KẾT NỐI GOOGLE SHEETS ===
credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
if not credentials_json:
    raise ValueError("Thiếu biến môi trường GOOGLE_CREDENTIALS_JSON")

credentials_dict = json.loads(credentials_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "memorysheet"
SHEET_NAME = "Sheet1"
spreadsheet = client.open(SPREADSHEET_NAME)
sheet = spreadsheet.worksheet(SHEET_NAME)

# === HÀM GHI NHỚ ===
def save_memory(user_id, content, note_type="khác"):
    time_str = datetime.now().isoformat()
    sheet.append_row([str(user_id), content, note_type, time_str])

# === LẤY GHI NHỚ ===
def get_memory(user_id, note_type=None):
    all_data = sheet.get_all_values()
    user_notes = []
    for row in all_data[1:]:
        if row[0] == str(user_id):
            note = {"content": row[1], "type": row[2], "time": row[3]}
            if note_type is None or note["type"] == note_type:
                user_notes.append(note)
    return user_notes

# === TÌM KIẾM GHI NHỚ ===
def search_memory(user_id, keyword):
    notes = get_memory(user_id)
    result = []
    keyword_lower = keyword.lower()
    for idx, note in enumerate(notes):
        if keyword_lower in note["content"].lower() or keyword_lower in note["type"].lower():
            result.append((idx, note))
    return result

# === XÓA TOÀN BỘ GHI NHỚ ===
def clear_memory(user_id):
    all_data = sheet.get_all_values()
    indexes_to_delete = []
    for idx, row in enumerate(all_data[1:], start=2):
        if row[0] == str(user_id):
            indexes_to_delete.append(idx)
    for i in reversed(indexes_to_delete):
        sheet.delete_rows(i)
    return bool(indexes_to_delete)

# === CẬP NHẬT LOẠI GHI NHỚ MỚI NHẤT ===
def update_latest_memory_type(user_id, note_type):
    all_data = sheet.get_all_values()
    user_rows = []
    for idx, row in enumerate(all_data[1:], start=2):
        if row[0] == str(user_id):
            user_rows.append((idx, row))
    if not user_rows:
        return False
    latest_row_idx = user_rows[-1][0]
    sheet.update_cell(latest_row_idx, 3, note_type)
    return True

# === LẤY GHI NHỚ GẦN NHẤT ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    notes.sort(key=lambda x: x["time"], reverse=True)
    recent = notes[:limit]
    return "\n".join(f"- ({n['type']}) {n['content']}" for n in recent)

# === XÓA GHI NHỚ THEO INDEX ===
def delete_memory_item(user_id, index):
    all_data = sheet.get_all_values()
    indexes_to_delete = []
    for idx, row in enumerate(all_data[1:], start=2):
        if row[0] == str(user_id):
            indexes_to_delete.append(idx)
    if 0 <= index < len(indexes_to_delete):
        target_row = indexes_to_delete[index]
        sheet.delete_rows(target_row)
        return True
    return False
