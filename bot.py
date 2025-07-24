import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Biến môi trường Zeabur

# Hàm gửi tin nhắn lên OpenRouter AI
def chat_with_ai(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",  # hoặc: "mistralai/mistral-7b-instruct"
        "messages": [{"role": "user", "content": user_message}],
        "temperature": 0.7
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code == 200:
        reply = response.json()['choices'][0]['message']['content']
        return reply.strip()
    else:
        return "⚠️ Tiểu Thiên đang gặp chút sự cố khi truy cập AI..."

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌟 Tiểu Thiên (AI) đã sẵn sàng! Hãy trò chuyện hoặc hỏi điều gì đó nhé.")

# Xử lý mọi tin nhắn → gửi lên AI → phản hồi
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    reply = chat_with_ai(user_input)
    await update.message.reply_text(reply)

# Khởi động bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))
    print("🤖 Tiểu Thiên (AI) đã khởi động!")
    app.run_polling()
