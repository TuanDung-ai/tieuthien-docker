import sqlite3

DB_PATH = "memory_full.db"

# Lấy toàn bộ dữ liệu từ SQLite (bảng du_an)
def get_du_an_sqlite():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ten, tien_do, ghi_chu, ngay_cap_nhat FROM du_an")
    rows = cursor.fetchall()
    conn.close()
    # Chuyển dữ liệu thành list dict (giống Supabase format)
    data = []
    for row in rows:
        data.append({
            "ten": row[0],
            "tien_do": row[1],
            "ghi_chu": row[2],
            "ngay_cap_nhat": row[3]
        })
    return data

# Lưu 1 bản ghi vào SQLite
def save_du_an_sqlite(data_dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO du_an (ten, tien_do, ghi_chu, ngay_cap_nhat)
        VALUES (?, ?, ?, ?)
    ''', (
        data_dict["ten"],
        data_dict["tien_do"],
        data_dict["ghi_chu"],
        data_dict["ngay_cap_nhat"]
    ))
    conn.commit()
    conn.close()
