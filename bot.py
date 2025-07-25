from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from ai_module import get_ai_response  # Import hàm AI từ file riêng

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Chào người dùng, bạn muốn Thiên Cơ giúp gì hôm nay?"
    ai_reply = get_ai_response(prompt)
    await update.message.reply_text(ai_reply)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🤖 Bot đang chạy với AI – Thiên Cơ sống dậy.")
    app.run_polling()
