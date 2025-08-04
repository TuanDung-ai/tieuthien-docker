# bot.py
import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder

# === TOKEN từ biến môi trường ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

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

def run_web_app():
    web_app.run(host="0.0.0.0", port=8080)

# === KHỞI ĐỘNG BOT + ĐỒNG BỘ ===
if __name__ == '__main__':
    threading.Thread(target=run_web_app).start()

    # === Đồng bộ Supabase → SQLite ===
    print("🔄 Đồng bộ Supabase → SQLite...")
    ensure_sqlite_cache()

    # === Đồng bộ SQLite → Supabase ===
    print("🔄 Đồng bộ SQLite → Supabase...")
    sync_sqlite_to_supabase()

    # === Khởi chạy bot Telegram ===
    app = ApplicationBuilder().token(TOKEN).build()
    register_handlers(app)

    print("🤖 Bot Thiên Cơ đã hồi sinh và vận hành...")
    app.run_polling()
