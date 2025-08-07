# handlers/start.py
from telegram import Update
from telegram.ext import ContextTypes
from modules.buttons import get_main_keyboard

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào chủ nhân, Thiên Cơ đã sẵn sàng!",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Thiên Cơ có thể giúp bạn ghi nhớ, xem lại ghi nhớ và xóa chúng đi.",
        reply_markup=get_main_keyboard()
    )
