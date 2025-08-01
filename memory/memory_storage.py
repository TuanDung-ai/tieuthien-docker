import sqlite3
from datetime import datetime
import os

DB_PATH = "memory_full.db"

# === KẾT NỐI DB ===
def get_conn():
    return sqlite3.connect(DB_PATH)

# === GHI NHỚ ===
def save_memory(user_id, content, note_type="khác"):
    time_str = datetime.now().isoformat()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO du_an (ten, tien_do, ghi_chu, ngay_cap_nhat)
        VALUES (?, ?, ?, ?)
    ''', (note_type, f"Ghi nhớ {user_id}", content, time_str))
    conn.commit()
    conn.close()

# === LẤY GHI NHỚ ===
def get_memory(user_id, note_type=None):
    conn = get_conn()
    cursor = conn.cursor()
    if note_type:
        cursor.execute('''
            SELECT ten, ghi_chu, ngay_cap_nhat FROM du_an
            WHERE ten=? AND tien_do LIKE ?
            ORDER BY ngay_cap_nhat DESC
        ''', (note_type, f"%{user_id}%"))
    else:
        cursor.execute('''
            SELECT ten, ghi_chu, ngay_cap_nhat FROM du_an
            WHERE tien_do LIKE ?
            ORDER BY ngay_cap_nhat DESC
        ''', (f"%{user_id}%",))
    rows = cursor.fetchall()
    conn.close()
    # Chuyển dữ liệu thành dict như trước
    return [
        {"note_type": r[0], "content": r[1], "time": r[2]}
        for r in rows
    ]

# === TÌM GHI NHỚ ===
def search_memory(user_id, keyword):
    notes = get_memory(user_id)
    keyword_lower = keyword.lower()
    return [(i, note) for i, note in enumerate(notes)
            if keyword_lower in note.get("content", "").lower() or keyword_lower in note.get("note_type", "").lower()]

# === XÓA TOÀN BỘ ===
def clear_memory(user_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM du_an WHERE tien_do LIKE ?
    ''', (f"%{user_id}%",))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

# === GHI NHỚ GẦN NHẤT (CHO PROMPT) ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    recent = notes[:limit]
    return "\n".join(f"- ({n['note_type']}) {n['content']}" for n in recent)
