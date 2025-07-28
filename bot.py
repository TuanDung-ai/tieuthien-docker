import os
from flask import Flask
import threading
from telegram.ext import ApplicationBuilder

# === Lấy TOKEN và hàm từ handlers ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
from handlers import register_handlers  # chỉ dòng này đủ để bot chạy

# === Web health check ===
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health_check():
    return "✅ Tiểu Thiên đang vận hành bình thường."

def run_web_app():
    web_app.run(host="0.0.0.0", port=8080)

# === Khởi động bot ===
if __name__ == '__main__':
    threading.Thread(target=run_web_app).start()
    app = ApplicationBuilder().token(TOKEN).build()
    register_handlers(app)
    print("🤖 Bot Thiên Cơ đã hồi sinh và vận hành...")
    app.run_polling()
