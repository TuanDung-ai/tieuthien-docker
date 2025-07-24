import os
import requests
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- Lấy token từ biến môi trường ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Kiểm tra biến môi trường
if not BOT_TOKEN or not OPENROUTER_API_KEY:
    print(f"⚠️ TELEGRAM_BOT_TOKEN: {BOT_TOKEN}")
    print(f"⚠️ OPENROUTER_API_KEY: {OPENROUTER_API_KEY}")
    raise ValueError("❌ Thiếu TELEGRAM_BOT_TOKEN hoặc OPENROUTER_API_KEY!")

# --- Hàm gọi OpenRouter AI ---
def chat_with_ai(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            reply = response.json()['choices'][0]['message']['content']
            return reply.strip()
        else:
            return f"⚠️ Lỗi AI [{response.status_code}]: {response.text}"
    except Exception as e:
        return f"⚠️ Tiểu Thiên gặp lỗi khi kết nối AI: {e}"

# --- Lệnh /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 Tiểu Thiên đã sẵn sàng! Hãy trò chuyện hoặc hỏi điều gì đó nhé.")

# --- Xử lý tin nhắn người dùng ---
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    reply = chat_with_ai(user_input)
    await update.message.reply_text(reply)

# --- Flask giữ online ---
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "✅ Tiểu Thiên đang hoạt động!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=8080)

# --- Khởi động song song Telegram + Flask ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))
    print("🤖 Tiểu Thiên đã khởi động!")
    app.run_polling()
