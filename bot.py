# bot.py
import os
import threading
import sys
import asyncio # Import asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder, Application # Import Application for type hinting

# === TOKEN từ biến môi trường ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Lấy cổng từ biến môi trường PORT mà Zeabur cung cấp, mặc định là 8080 cho môi trường local
PORT = int(os.getenv("PORT", 8080))

# === IMPORT các hàm ===
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
def run_telegram_bot(app: Application): # Nhận đối tượng app
    print("DEBUG: Bắt đầu luồng bot Telegram...")
    try:
        if not TOKEN:
            print("LỖI: TELEGRAM_BOT_TOKEN không được thiết lập! Bot Telegram sẽ không chạy.", file=sys.stderr)
            return # Exit thread if token is missing

        print("DEBUG: Đăng ký handlers cho bot Telegram...")
        register_handlers(app) # Đăng ký handlers trên đối tượng app đã được truyền vào

        # Tạo và thiết lập một event loop mới cho luồng này
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print("🤖 Bot Thiên Cơ đã hồi sinh và vận hành (polling)...")
        # Chạy polling. app.run_polling() sẽ tự quản lý event loop của nó.
        # Đảm bảo nó được chạy trong luồng có event loop đã được thiết lập.
        app.run_polling() # Đây là phương thức đúng để khởi động polling cho PTB v20+

    except Exception as e:
        print(f"LỖI NGHIÊM TRỌNG khi khởi động bot Telegram: {e}", file=sys.stderr)
        # sys.exit(1) # Cân nhắc thoát toàn bộ ứng dụng nếu bot Telegram crash

# === KHỞI ĐỘNG ỨNG DỤNG ===
if __name__ == '__main__':
    print("DEBUG: Bắt đầu quá trình khởi động ứng dụng chính...")
    try:
        # Khởi tạo đối tượng ApplicationBuilder ở đây để truyền cho luồng Telegram
        telegram_app = ApplicationBuilder().token(TOKEN).build()

        # === Đồng bộ Supabase → SQLite ===
        print("DEBUG: Bắt đầu đồng bộ Supabase → SQLite...")
        ensure_sqlite_cache()
        print("DEBUG: Đồng bộ Supabase → SQLite hoàn tất.")

        # === Đồng bộ SQLite → Supabase ===
        print("DEBUG: Bắt đầu đồng bộ SQLite → Supabase...")
        sync_sqlite_to_supabase()
        print("DEBUG: Đồng bộ SQLite → Supabase hoàn tất.")

        # Khởi động bot Telegram trong một luồng riêng, truyền đối tượng app
        print("DEBUG: Khởi động luồng bot Telegram...")
        telegram_thread = threading.Thread(target=run_telegram_bot, args=(telegram_app,))
        telegram_thread.daemon = True
        telegram_thread.start()
        print("DEBUG: Luồng bot Telegram đã được khởi tạo.")

        # Khởi động Flask web app trong luồng chính
        print(f"DEBUG: Bắt đầu Flask web server trên cổng {PORT}...")
        web_app.run(host="0.0.0.0", port=PORT)
        print("DEBUG: Flask web server đã dừng (có thể do lỗi hoặc shutdown).")
    except Exception as e:
        print(f"LỖI NGHIÊM TRỌNG khi khởi động ứng dụng chính: {e}", file=sys.stderr)
        sys.exit(1)
