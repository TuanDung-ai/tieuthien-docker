import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Lấy token từ biến môi trường
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# Hàm gọi GPT Free qua OpenRouter
def get_ai_response(user_prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": "Bạn là Thiên Cơ – AI trợ lý cá nhân, trầm ổn – chính xác – hài hước nhẹ. Trả lời ngắn gọn, có gợi ý."},
        {"role": "user", "content": user_prompt}
    ]
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 400
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("Lỗi AI:", e)
        return "Thiên Cơ gặp trục trặc nhẹ... thử lại sau nhé."

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Chào người dùng, bạn muốn Thiên Cơ giúp gì hôm nay?"
    ai_reply = get_ai_response(prompt)
    await update.message.reply_text(ai_reply)

# Lệnh /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🌀 Thiên Cơ lắng nghe...\n\n"
        "Lệnh khả dụng:\n"
        "/start – Bắt đầu trò chuyện\n"
        "/help – Danh sách lệnh\n"
        "(Hoặc chat bất kỳ để nhận phản hồi từ Thiên Cơ)"
    )
    await update.message.reply_text(msg)

# Phản hồi mọi tin nhắn văn bản
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    ai_reply = get_ai_response(user_text)
    await update.message.reply_text(ai_reply)

# Khởi chạy bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot Thiên Cơ đang hoạt động...")
    app.run_polling()
