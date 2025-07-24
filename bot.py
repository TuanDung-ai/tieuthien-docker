import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Lấy biến môi trường từ Zeabur
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Đúng tên biến bạn đã cài
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Kiểm tra biến môi trường
if not BOT_TOKEN or not OPENROUTER_API_KEY:
    print(f"⚠️ TELEGRAM_BOT_TOKEN: {BOT_TOKEN}")
    print(f"⚠️ OPENROUTER_API_KEY: {OPENROUTER_API_KEY}")
    raise ValueError("❌ Thiếu TELEGRAM_BOT_TOKEN hoặc OPENROUTER_API_KEY!")

# Hàm gửi tin nhắn lên OpenRouter AI
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
            print(f"⚠️ API lỗi: {response.status_code} - {response.text}")
            return "⚠️ Tiểu Thiên gặp lỗi khi truy cập AI..."
    except Exception as e:
        print(f"❌ Lỗi kết nối OpenRouter: {e}")
        return "⚠️ Không thể kết nối tới AI. Vui lòng thử lại sau."

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 Tiểu Thiên (AI) đã sẵn sàng! Hãy trò chuyện hoặc hỏi điều gì đó nhé.")

# Xử lý mọi tin nhắn văn bản
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    reply = chat_with_ai(user_input)
    await update.message.reply_text(reply)

# Khởi chạy bot
if __name__ == "__main__":
    print("🔄 Đang khởi động Tiểu Thiên...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))
    print("✅ Tiểu Thiên đã sẵn sàng hoạt động.")
    app.run_polling()
