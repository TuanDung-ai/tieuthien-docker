import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Lấy token từ biến môi trường (Zeabur đã cấu hình)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Hàm xử lý lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Tiểu Thiên đã sẵn sàng phục vụ bạn rồi! Gõ vài dòng thử nhé.")

# Hàm xử lý tin nhắn văn bản – có chọn lọc
async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    # Danh sách từ khóa để bot phản hồi
    keywords = ["chào", "giúp", "thiên", "bot", "?", "bạn"]
    
    if any(keyword in user_text for keyword in keywords):
        await update.message.reply_text("👋 Tiểu Thiên nghe đây, bạn cần gì?")
    else:
        # Không phản hồi nếu không có từ khóa – tránh lặp
        pass

# Chạy bot bằng polling
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))
    print("🤖 Tiểu Thiên đã khởi động!")
    app.run_polling()
