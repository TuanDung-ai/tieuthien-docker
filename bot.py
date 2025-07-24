import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tiểu Thiên đã online!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot started...")
    app.run_polling()
