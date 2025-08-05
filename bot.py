# bot.py
import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder

# === TOKEN từ biến môi trường ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Lấy cổng từ biến môi trường PORT mà Zeabur cung cấp, mặc định là 8080 cho môi trường local
PORT = int(os.getenv("PORT", 8080))

# === IMPORT các hàm ===
from modules.handlers import register_handlers
from memory.sync_on_startup import ensure_sqlite_cache
from memory.sync_to_cloud import sync_sqlite_to_supabase

# === Web health check ===
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health_check():
    return "✅ Tiểu Thiên đang vận hành bình thường."

# Hàm để chạy bot Telegram (trong một luồng riêng)
def run_telegram_bot():
    print("🤖 Bot Thiên Cơ đã hồi sinh và vận hành...")
    app = ApplicationBuilder().token(TOKEN).build()
    register_handlers(app)
    app.run_polling() # Đây là hàm chặn cho bot Telegram

# === KHỞI ĐỘNG ỨNG DỤNG ===
if __name__ == '__main__':
    # === Đồng bộ Supabase → SQLite ===
    print("🔄 Đồng bộ Supabase → SQLite...")
    ensure_sqlite_cache()

    # === Đồng bộ SQLite → Supabase ===
    print("🔄 Đồng bộ SQLite → Supabase...")
    sync_sqlite_to_supabase()

    # Khởi động bot Telegram trong một luồng riêng
    telegram_thread = threading.Thread(target=run_telegram_bot)
    telegram_thread.start()

    # Khởi động Flask web app trong luồng chính
    # Flask app sẽ lắng nghe trên cổng mà Zeabur cung cấp (biến môi trường PORT)
    print(f"🌐 Bắt đầu web server trên cổng {PORT} để Zeabur kiểm tra trạng thái...")
    web_app.run(host="0.0.0.0", port=PORT)
