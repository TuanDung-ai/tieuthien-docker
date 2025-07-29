import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder

# === Lấy TOKEN từ biến môi trường ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === Import hàm đăng ký handlers từ modules ===
from modules.handlers import register_handlers

# === Web health check ===
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health_check():
    return "✅ Tiểu Thiên đang vận hành bình thường."

def run_web_app():
    web_app.run(host="0.0.0.0", port=8080)

# === Khởi động bot Telegram + Web ===
if __name__ == '__main__':
    threading.Thread(target=run_web_app).start()

    app = ApplicationBuilder().token(TOKEN).build()
    register_handlers(app)

    print("🤖 Bot Thiên Cơ đã hồi sinh và vận hành...")
    app.run_polling()
