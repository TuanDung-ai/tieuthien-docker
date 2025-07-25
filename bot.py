# bot.py – phiên bản sạch – chuẩn bị tích hợp Thiên Cơ

import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Lấy token từ biến môi trường hoặc ghi trực tiếp
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Khuyên dùng .env hoặc config Zeabur

# Hàm phản hồi lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Thiên Cơ đã sẵn sàng. Chờ lệnh...")

# Khởi chạy bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🤖 Bot đang chạy... Thiên Cơ khởi động.")
    app.run_polling()
