import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# ✅ Sử dụng memory_manager thay vì memory_storage
from memory.memory_manager import (
    save_memory, get_memory, search_memory,
    clear_memory, get_recent_memories_for_prompt
)

from modules.ai_module import get_ai_response_with_memory

user_states = {}  # user_id → trạng thái (ghi nhớ)

# === GIAO DIỆN NÚT ===
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Ghi nhớ", callback_data='note'),
            InlineKeyboardButton("📅 Lịch", callback_data='calendar'),
            InlineKeyboardButton("🌷 Thư giãn", callback_data='relax')
        ],
        [
            InlineKeyboardButton("📖 Xem nhớ", callback_data='view'),
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

# === PHẢN HỒI AI ===
def format_ai_response(text):
    return (
        "🌀 Thiên Cơ phản hồi:\n\n"
        f"{text.strip()}\n\n"
        "✨ Bạn muốn ghi nhớ, xem lịch, hay thư giãn?"
    )

# === HANDLERS CHÍNH ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào chủ nhân, Tiểu Thiên đã sẵn sàng!",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Tiểu Thiên có thể giúp bạn ghi nhớ, xem lại ghi nhớ và xóa chúng đi.",
        reply_markup=get_main_keyboard()
    )

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
    ai_reply = await get_ai_response_with_memory(user_id, user_text)
    await update.message.reply_text(ai_reply, reply_markup=get_main_keyboard())

# === XỬ LÝ NÚT BẤM ===
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    data = query.data

    if data == 'note':
        await query.edit_message_text("📝 Chọn loại ghi nhớ:", reply_markup=get_note_type_keyboard())
    elif data.startswith("type_"):
        note_type = data.split("_", 1)[1]
        user_states[user_id] = {"awaiting_note": True, "type": note_type}
        await query.edit_message_text(f"✍️ Gõ nội dung để ghi nhớ dạng '{note_type}':")
    elif data == 'view':
        memories = get_memory(user_id)
        if memories:
            reply_text = "📖 Những ghi nhớ của bạn:\n\n"
            for mem in memories:
                reply_text += f"- ({mem['note_type']}) {mem['content']}\n"
            await query.edit_message_text(reply_text, reply_markup=get_main_keyboard())
        else:
            await query.edit_message_text("Bạn chưa có ghi nhớ nào.", reply_markup=get_main_keyboard())
    elif data == 'clear_all':
        clear_memory(user_id)
        await query.edit_message_text("🗑️ Đã xóa toàn bộ ghi nhớ.", reply_markup=get_main_keyboard())
    else:
        await query.edit_message_text("⚠️ Chức năng chưa khả dụng.", reply_markup=get_main_keyboard())

# === ĐĂNG KÝ HANDLERS ===
def register_handlers(app: Application):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
