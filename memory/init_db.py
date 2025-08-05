# memory/init_db.py
import sqlite3
import os

# Sử dụng DB_FILE từ db_sqlite.py để đảm bảo đường dẫn nhất quán
# Vì init_db.py nằm cùng cấp với db_sqlite.py, chúng ta có thể dùng đường dẫn tương đối
# hoặc đảm bảo rằng DB_PATH ở đây khớp với DB_FILE trong db_sqlite.py
# Tốt nhất là nên lấy đường dẫn từ db_sqlite để tránh sai sót.
# Tuy nhiên, vì init_db.py có thể được chạy độc lập, chúng ta giữ nguyên DB_PATH.
# Đảm bảo DB_PATH này trỏ đến cùng một file memory_full.db như trong db_sqlite.py
DB_PATH = os.path.join(os.path.dirname(__file__), "memory_full.db")

def init_sqlite_db():
    # Kiểm tra nếu database đã tồn tại
    if os.path.exists(DB_PATH):
        print("✅ SQLite đã tồn tại. Kiểm tra và tạo bảng nếu thiếu.")
        # Nếu DB đã tồn tại, chúng ta vẫn cần đảm bảo bảng 'memories' có mặt
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS memories (
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                note_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        print("✅ Đã kiểm tra và đảm bảo bảng 'memories' tồn tại.")
        return

    # Nếu database chưa tồn tại, tạo mới và tất cả các bảng
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Bảng du_an
    cursor.execute('''
        CREATE TABLE du_an (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten TEXT,
            tien_do TEXT,
            ghi_chu TEXT,
            ngay_cap_nhat TEXT
        )
    ''')

    # Bảng user_info
    cursor.execute('''
        CREATE TABLE user_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ten TEXT,
            tuoi INTEGER,
            email TEXT,
            so_thich TEXT,
            so_dien_thoai TEXT
        )
    ''')

    # Bảng lich_trinh
    cursor.execute('''
        CREATE TABLE lich_trinh (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ngay TEXT,
            thoi_gian TEXT,
            noi_dung TEXT,
            lap_lai TEXT
        )
    ''')

    # Bảng kinh_te
    cursor.execute('''
        CREATE TABLE kinh_te (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            loai TEXT,
            so_tien INTEGER,
            ghi_chu TEXT,
            ngay TEXT
        )
    ''')

    # Bảng ghi_chu
    cursor.execute('''
        CREATE TABLE ghi_chu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tieu_de TEXT,
            noi_dung TEXT,
            ngay_luu TEXT
        )
    ''')

    # THÊM BẢNG 'memories' VÀO ĐÂY!
    cursor.execute(f"""
        CREATE TABLE memories (
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            note_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Đã khởi tạo file SQLite và tất cả các bảng thành công.")

if __name__ == "__main__":
    init_sqlite_db()
