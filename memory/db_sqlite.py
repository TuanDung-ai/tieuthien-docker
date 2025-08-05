# memory/db_sqlite.py
import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "memory_full.db")
TABLE_NAME = "memories"

def get_conn():
    """Tạo hoặc kết nối đến database SQLite."""
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    """Khởi tạo database và tạo bảng nếu chưa tồn tại."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            note_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_memory(user_id, content, note_type=None):
    """Lưu một ghi nhớ mới vào SQLite."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {TABLE_NAME} (user_id, content, note_type)
        VALUES (?, ?, ?)
    """, (user_id, content, note_type))
    conn.commit()
    conn.close()

def get_memory(user_id, note_type=None):
    """Lấy các ghi nhớ từ SQLite dựa trên user_id và note_type."""
    conn = get_conn()
    cursor = conn.cursor()
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_id = ?"
    params = [user_id]
    
    if note_type:
        query += " AND note_type = ?"
        params.append(note_type)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Chuyển đổi dữ liệu sang format dễ dùng hơn
    results = []
    for row in rows:
        results.append({
            'user_id': row[0],
            'content': row[1],
            'note_type': row[2],
            'timestamp': row[3]
        })
    return results

def delete_memory(user_id):
    """Xóa tất cả các ghi nhớ của một user_id."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_all_local_memories():
    """Lấy tất cả các ghi nhớ trong SQLite (dùng cho đồng bộ)."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            'user_id': row[0],
            'content': row[1],
            'note_type': row[2],
            'timestamp': row[3]
        })
    return results
