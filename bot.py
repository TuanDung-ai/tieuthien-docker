# bot.py
import os
import threading
import sys # Import sys for exiting
from flask import Flask
from telegram.ext import ApplicationBuilder

# === TOKEN từ biến môi trường ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Lấy cổng từ biến môi trường PORT mà Zeabur cung cấp, mặc định là 8080 cho môi trường local
PORT = int(os.getenv("PORT", 8080))

# === IMPORT các hàm ===
# Đảm bảo các import này không gây lỗi ngay lập tức
try:
    from modules.handlers import register_handlers
    from memory.sync_on_startup import ensure_sqlite_cache
    from memory.sync_to_cloud import sync_sqlite_to_supabase
    print("DEBUG: Import các module thành công.")
except ImportError as e:
    print(f"LỖI KHỞI ĐỘNG: Không thể import module: {e}", file=sys.stderr)
    sys.exit(1) # Thoát ngay nếu không import được

# === Web health check ===
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health_check():
    return "✅ Tiểu Thiên đang vận hành bình thường."

# Hàm để chạy bot Telegram (trong một luồng riêng)
def run_telegram_bot():
    print("DEBUG: Bắt đầu luồng bot Telegram...")
    try:
        if not TOKEN:
            print("LỖI: TELEGRAM_BOT_TOKEN không được thiết lập! Bot Telegram sẽ không chạy.", file=sys.stderr)
            return # Exit thread if token is missing

        print("DEBUG: Xây dựng ứng dụng Telegram bot...")
        app = ApplicationBuilder().token(TOKEN).build()
        print("DEBUG: Đăng ký handlers cho bot Telegram...")
        register_handlers(app)
        print("🤖 Bot Thiên Cơ đã hồi sinh và vận hành (polling)...")
        app.run_polling() # This is a blocking call for the Telegram bot
    except Exception as e:
        print(f"LỖI NGHIÊM TRỌNG khi khởi động bot Telegram: {e}", file=sys.stderr)
        # sys.exit(1) # Có thể gây tắt luôn web server, cân nhắc kỹ

# === KHỞI ĐỘNG ỨNG DỤNG ===
if __name__ == '__main__':
    print("DEBUG: Bắt đầu quá trình khởi động ứng dụng chính...")
    try:
        # === Đồng bộ Supabase → SQLite ===
        print("DEBUG: Bắt đầu đồng bộ Supabase → SQLite...")
        ensure_sqlite_cache() # Hàm này cần có log riêng bên trong nó
        print("DEBUG: Đồng bộ Supabase → SQLite hoàn tất.")

        # === Đồng bộ SQLite → Supabase ===
        print("DEBUG: Bắt đầu đồng bộ SQLite → Supabase...")
        sync_sqlite_to_supabase() # Hàm này cần có log riêng bên trong nó
        print("DEBUG: Đồng bộ SQLite → Supabase hoàn tất.")

        # Khởi động bot Telegram trong một luồng riêng
        print("DEBUG: Khởi động luồng bot Telegram...")
        telegram_thread = threading.Thread(target=run_telegram_bot)
        telegram_thread.daemon = True # Cho phép chương trình chính thoát ngay cả khi luồng này đang chạy
        telegram_thread.start()
        print("DEBUG: Luồng bot Telegram đã được khởi tạo.")

        # Khởi động Flask web app trong luồng chính
        # Flask app sẽ lắng nghe trên cổng mà Zeabur cung cấp (biến môi trường PORT)
        print(f"DEBUG: Bắt đầu Flask web server trên cổng {PORT}...")
        web_app.run(host="0.0.0.0", port=PORT)
        print("DEBUG: Flask web server đã dừng (có thể do lỗi hoặc shutdown).") # Dòng này chỉ in ra nếu web_app.run() kết thúc
    except Exception as e:
        print(f"LỖI NGHIÊM TRỌNG khi khởi động ứng dụng chính: {e}", file=sys.stderr)
        sys.exit(1) # Thoát với mã lỗi để báo hiệu Zeabur rằng khởi động thất bại

