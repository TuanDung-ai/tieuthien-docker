# modules/handlers.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from memory.memory_manager import (
    save_memory, get_memory, delete_memory, clear_memory
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

# === HANDLERS CHÍNH ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    state = user_states.get(user_id)
    if state and state.get("awaiting_note"):
        note_type = user_states[user_id]["type"]
        
        # Gọi hàm save_memory để lưu nội dung vào Supabase
        save_memory(user_id, user_text, note_type)
        
        # Xóa trạng thái sau khi lưu
        user_states.pop(user_id)
        
        # Phản hồi lại người dùng và hiển thị bàn phím chính
        await update.message.reply_text(f"✅ Ghi nhớ của bạn đã được lưu với loại: '{note_type}'.", reply_markup=get_main_keyboard())
    else:
        # Phản hồi AI nếu không phải là ghi nhớ
        ai_reply = await get_ai_response_with_memory(user_id, user_text)
        await update.message.reply_text(ai_reply, reply_markup=get_main_keyboard())


# === XỬ LÝ NÚT BẤM ===
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            for i, mem in enumerate(memories):
                reply_text += f"{i+1}. ({mem.get('note_type', 'khác')}) {mem.get('content', 'không có nội dung')}\n"
            await query.edit_message_text(reply_text, reply_markup=get_main_keyboard())
        else:
            await query.edit_message_text("Bạn chưa có ghi nhớ nào.", reply_markup=get_main_keyboard())
    elif data == 'clear_all':
        clear_memory(user_id)
        await query.edit_message_text("🗑️ Đã xóa toàn bộ ghi nhớ.", reply_markup=get_main_keyboard())
    else:
        # Trả lại bàn phím chính nếu data không khớp
        await query.edit_message_text("⚠️ Lỗi: Chức năng không hợp lệ.", reply_markup=get_main_keyboard())

# === ĐĂNG KÝ HANDLERS ===
def register_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
