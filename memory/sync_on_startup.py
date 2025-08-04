import os
import sqlite3
from memory.db_supabase import fetch_du_an_supabase
from memory.db_sqlite import save_du_an_sqlite
from memory.init_db import init_sqlite_db

DB_PATH = "memory_full.db"

# Kiểm tra file SQLite có tồn tại và chứa dữ liệu không
def is_sqlite_ready():
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM du_an")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except:
        return False

# Đồng bộ lại SQLite từ Supabase (nếu mất)
def sync_sqlite_from_supabase():
    print("⚠️ Cache SQLite trống hoặc mất → khôi phục từ Supabase...")
    du_an_data = fetch_du_an_supabase()
    if not du_an_data:
        print("❌ Supabase cũng không có dữ liệu du_an.")
        return

    for row in du_an_data:
        save_du_an_sqlite(row)
    print(f"✅ Khôi phục {len(du_an_data)} dòng dự án vào SQLite.")

# Hàm khởi động – gọi khi bot start
def ensure_sqlite_cache():
    if is_sqlite_ready():
        print("✅ SQLite cache sẵn sàng.")
    else:
        init_sqlite_db()
        sync_sqlite_from_supabase()

# Gọi thử nếu chạy file này trực tiếp
if __name__ == "__main__":
    ensure_sqlite_cache()
