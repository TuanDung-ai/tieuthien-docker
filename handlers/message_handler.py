# handlers/message_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from modules.ai_module import get_ai_response_with_memory


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if not text:
        await update.message.reply_text("⚠️ Tin nhắn trống.")
        return

    reply = await get_ai_response_with_memory(user_id, text)
    await update.message.reply_text(reply)
