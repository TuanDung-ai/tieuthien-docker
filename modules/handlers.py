# modules/handlers.py
import os
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from memory.memory_manager import (
    save_memory, get_memory, delete_memory
)
from modules.ai_module import get_ai_response_with_memory
from modules.memory_api_helper import get_memory_from_api, save_memory_to_api

# === API KEY OpenRouter ===
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
user_states = {}

# === GIAO DIỆN NÚT ===
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Ghi nhớ", callback_data='note'),
            InlineKeyboardButton("📖 Xem nhớ", callback_data='view')
        ],
        [
            InlineKeyboardButton("🗑️ Xóa hết", callback_data='clear_all')
        ]
    ])

def get_note_type_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 Tâm sự", callback_data='type_tamsu'),
            InlineKeyboardButton("⏰ Nhắc nhở", callback_data='type_nhacnho')
        ],
        [
            InlineKeyboardButton("💡 Ý tưởng", callback_data='type_ytuong'),
            InlineKeyboardButton("📂 Cá nhân", callback_data='type_canhan')
        ]
    ])


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text
    
    # Xử lý khi đang chờ ghi nhớ
    if user_states.get(user_id, {}).get("awaiting_note"):
        note_type = user_states[user_id]["type"]
        save_memory(user_id, user_text, note_type)
        user_states[user_id] = {}
        await update.message.reply_text("✅ Ghi nhớ của bạn đã được lưu.")
        return
        
    # Phản hồi AI
    ai_reply = await get_ai_response_with_memory(user_text)
    await update.message.reply_text(ai_reply, reply_markup=get_main_keyboard())

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    await query.answer()

    if data == 'note':
        user_states[user_id] = {"awaiting_note": True}
        await query.edit_message_text(
            "Bạn muốn ghi nhớ loại gì?",
            reply_markup=get_note_type_keyboard()
        )
    elif data.startswith('type_'):
        note_type = data.split('_')[1]
        user_states[user_id]["type"] = note_type
        await query.edit_message_text(f"Nhập nội dung {note_type} của bạn:")
    elif data == 'view':
        # Gọi hàm get_memory đã được tối ưu
        memories = get_memory(user_id)
        if memories:
            reply_text = "📖 **Những ghi nhớ của bạn:**\n\n"
            for mem in memories:
                reply_text += f"- **{mem['note_type']}:** {mem['content']}\n"
        else:
            reply_text = "📖 Bạn chưa có ghi nhớ nào."
        await query.edit_message_text(reply_text, reply_markup=get_main_keyboard())
    elif data == 'clear_all':
        delete_memory(user_id)
        await query.edit_message_text("🗑️ Đã xóa toàn bộ ghi nhớ.")
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Chào chủ nhân, Tiểu Thiên đã sẵn sàng!", reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tiểu Thiên có thể giúp bạn ghi nhớ, xem lại ghi nhớ và xóa chúng đi.", reply_markup=get_main_keyboard())

def main() -> None:
    # (giữ nguyên logic khởi chạy bot)
    # ...
    # handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)
