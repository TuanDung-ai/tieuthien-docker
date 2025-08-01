import sqlite3
import os

DB_PATH = "memory_full.db"

def init_sqlite_db():
    if os.path.exists(DB_PATH):
        print("✅ SQLite đã tồn tại, bỏ qua khởi tạo.")
        return

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

    conn.commit()
    conn.close()
    print("✅ Đã khởi tạo file SQLite và bảng thành công.")

if __name__ == "__main__":
    init_sqlite_db()
