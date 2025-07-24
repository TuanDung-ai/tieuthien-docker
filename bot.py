import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tiểu Thiên sẵn sàng rồi, bạn cần gì nè?")

async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Bạn vừa nói: {update.message.text}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_message))
    print("Bot started...")
    app.run_polling()
