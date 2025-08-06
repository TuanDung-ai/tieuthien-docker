# modules/handlers.py
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from memory.memory_manager import (
    save_memory, get_memory, clear_memory, delete_single_memory
)
from modules.ai_module import get_ai_response_with_memory

user_states = {}

# === GIAO DIỆN NÚT ===
def get_main_keyboard():
    """Bỏ nút Thư giãn và cập nhật tên bot."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Ghi nhớ", callback_data='note'),
            InlineKeyboardButton("📅 Lịch", callback_data='calendar')
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
        "Chào chủ nhân, Thiên Cơ đã sẵn sàng!",
        reply_markup=get_main_keyboard()
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Thiên Cơ có thể giúp bạn ghi nhớ, xem lại ghi nhớ và xóa chúng đi.",
        reply_markup=get_main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text
    
    state = user_states.get(user_id)
    
    if state and state.get("awaiting_note"):
        note_type = state.get("type")
        
        save_memory(user_id, user_text, note_type)
        user_states.pop(user_id)
        
        await update.message.reply_text(
            f"✅ Ghi nhớ của bạn đã được Thiên Cơ lưu lại với loại: '{note_type}'.",
            reply_markup=get_main_keyboard()
        )
    else:
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
        await query.edit_message_text(f"✍️ Gõ nội dung để Thiên Cơ ghi nhớ dạng '{note_type}':")
    elif data == 'view':
        memories = get_memory(user_id)
        if memories:
            keyboard = []
            reply_text = "📖 Những ghi nhớ của bạn:\n\n"
            for mem in memories:
                note_id = mem.get('id')
                content_preview = mem.get('content', '')[:20] + '...' if len(mem.get('content', '')) > 20 else mem.get('content', '')
                reply_text += f"ID: {note_id} - ({mem.get('note_type', 'khác')}) {content_preview}\n"
                keyboard.append([InlineKeyboardButton(f"🗑️ Xóa ID: {note_id}", callback_data=f"delete_{note_id}")])

            keyboard.append([InlineKeyboardButton("⬅️ Quay lại", callback_data='back_to_main')])
            await query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            current_text = "Bạn chưa có ghi nhớ nào."
            if query.message.text != current_text:
                await query.edit_message_text(current_text, reply_markup=get_main_keyboard())
    elif data == 'clear_all':
        clear_memory(user_id)
        await query.edit_message_text("🗑️ Đã xóa toàn bộ ghi nhớ.", reply_markup=get_main_keyboard())
    elif data.startswith("delete_"):
        try:
            note_id = int(data.split("_")[1])
            delete_single_memory(user_id, note_id)
            await query.edit_message_text(f"✅ Đã xóa ghi nhớ có ID: {note_id}.", reply_markup=get_main_keyboard())
        except (ValueError, IndexError):
            await query.edit_message_text("Lỗi khi xóa ghi nhớ.", reply_markup=get_main_keyboard())
    elif data == 'back_to_main':
        await query.edit_message_text("✨ Bạn muốn Thiên Cơ làm gì tiếp?", reply_markup=get_main_keyboard())
    else:
        await query.edit_message_text("Chức năng không hợp lệ. Bạn muốn Thiên Cơ làm gì tiếp?", reply_markup=get_main_keyboard())

# === ĐĂNG KÝ HANDLERS ===
def register_handlers(app: Application):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
