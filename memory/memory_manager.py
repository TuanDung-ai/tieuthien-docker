from db_sqlite import get_du_an_sqlite, save_du_an_sqlite
from db_supabase import fetch_du_an_supabase, insert_du_an_supabase

# Lấy dữ liệu ưu tiên từ cache
def get_du_an():
    local_data = get_du_an_sqlite()
    if local_data:
        return local_data
    # Nếu cache trống → lấy từ Supabase → cache lại
    cloud_data = fetch_du_an_supabase()
    for row in cloud_data:
        save_du_an_sqlite(row)  # Ghi lại vào SQLite
    return cloud_data

# Ghi dữ liệu vào cả hai nơi
def add_du_an(data_dict):
    save_du_an_sqlite(data_dict)
    insert_du_an_supabase(data_dict)
