# Write the corrected handlers.py code to a file for download
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from modules.sheets import (
    save_memory, get_memory, search_memory,
    clear_memory, delete_memory_item, update_latest_memory_type,
    get_recent_memories_for_prompt
)

# === API KEY OpenRouter ===
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
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
    lines = text.strip().split('\\n')
    short_text = " ".join(line.strip() for line in lines if line.strip())
    if len(short_text) > 500:
        short_text = short_text[:497] + "..."
    footer = "\\n\\n💡 Bạn cần gì tiếp theo? Ví dụ: '📝 Ghi nhớ', '📅 Lịch', '🌷 Thư giãn'."
    return f"😎 Thiên Cơ:\\n\\n{short_text}{footer}"

def get_ai_response(user_prompt, user_id=None):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    memory_context = ""
    if user_id:
        mems = get_recent_memories_for_prompt(user_id)
        if mems:
            memory_context = f"Người dùng trước đó đã ghi nhớ:\\n{mems}\\n\\n"
    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là Thiên Cơ – AI trợ lý cá nhân đáng tin cậy. "
                "Luôn trả lời trầm ổn, chính xác, tối đa 3 câu, có thể sử dụng dữ kiện cũ."
            )
        },
        {
            "role": "user",
            "content": memory_context + user_prompt
        }
    ]
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 400
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"]
        return format_ai_response(raw_text)
    except Exception as e:
        print("Lỗi AI:", e)
        return "⚠️ Thiên Cơ gặp trục trặc nhẹ... thử lại sau nhé."

# === LỆNH CƠ BẢN ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Chào người dùng, bạn muốn Thiên Cơ giúp gì hôm nay?"
    ai_reply = get_ai_response(prompt, user_id=update.message.from_user.id)
    await update.message.reply_text(ai_reply, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🌀 Thiên Cơ lắng nghe...\\n\\n"
        "Lệnh khả dụng:\\n"
        "/start – Bắt đầu trò chuyện\\n"
        "/help – Danh sách lệnh\\n"
        "/xem_ghi_nho – Xem lại ký ức\\n"
        "/xoa_ghi_nho_all – Xóa toàn bộ ghi nhớ\\n"
        "/tim_ghi_nho <từ khóa> – Tìm ghi nhớ\\n"
        "(Hoặc chat bất kỳ để trò chuyện cùng Thiên Cơ)"
    )
    await update.message.reply_text(msg)

# === XỬ LÝ GHI NHỚ ===
async def xem_ghi_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    notes = get_memory(user_id)
    if not notes:
        msg = "📭 Bạn chưa có ghi nhớ nào."
        if update.message:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.edit_message_text(msg)
        return

    for real_index, n in enumerate(notes[-10:], start=len(notes)-10):
        note_type = n.get("type", "khác")
        content = n.get("content", "")
        text = f"{real_index+1}. ({note_type}) {content}"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Xóa", callback_data=f"delete_{real_index}"),
            InlineKeyboardButton("👁️ Xem", callback_data=f"view_{real_index}")
        ]])
        if update.message:
            await update.message.reply_text(text, reply_markup=keyboard)
        else:
            await update.callback_query.message.reply_text(text, reply_markup=keyboard)

async def xoa_ghi_nho_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cleared = clear_memory(update.message.from_user.id)
    msg = "🗑️ Đã xóa toàn bộ ghi nhớ." if cleared else "⚠️ Không có ghi nhớ nào để xóa."
    await update.message.reply_text(msg)

async def tim_ghi_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Dùng như sau: /tim_ghi_nho từ_khóa")
        return
    keyword = " ".join(args)
    results = search_memory(update.message.from_user.id, keyword)
    if not results:
        await update.message.reply_text("🔍 Không tìm thấy ghi nhớ phù hợp.")
        return
    lines = []
    for i, (_, n) in enumerate(results[:10]):
        note_type = n.get("type", "khác")
        content = n.get("content", "")
        lines.append(f"{i+1}. ({note_type}) {content}")
    await update.message.reply_text("\\n".join(lines))

# === NHẬN TIN NHẮN ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id, {})
    if state.get("awaiting_note"):
        note_type = state.get("type", "khác")
        save_memory(user_id, text, note_type)
        await update.message.reply_text(f"✅ Đã lưu ghi nhớ dạng '{note_type}'.", reply_markup=get_main_keyboard())
        user_states.pop(user_id, None)
    else:
        ai_reply = get_ai_response(text, user_id=user_id)
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
        await xem_ghi_nho(update, context)
    elif data == 'clear_all':
        cleared = clear_memory(user_id)
        msg = "🗑️ Đã xóa toàn bộ ghi nhớ." if cleared else "⚠️ Không có gì để xóa."
        await query.edit_message_text(msg)
    elif data.startswith("delete_") or data.startswith("view_"):
        index = int(data.split("_")[1])
        notes = get_memory(user_id)
        if index >= len(notes):
            await query.edit_message_text("⚠️ Ghi nhớ này không còn tồn tại hoặc đã bị xóa.")
            return
        if data.startswith("delete_"):
            deleted = delete_memory_item(user_id, index)
            msg = "🗑️ Ghi nhớ đã được xóa." if deleted else "⚠️ Không thể xóa ghi nhớ này."
            await query.edit_message_text(msg)
        else:
            note = notes[index]
            await query.edit_message_text(f"👁️ ({note.get('type', 'khác')}) {note.get('content', '')}")
    else:
        await query.edit_message_text("⚠️ Chức năng chưa khả dụng.")

# === ĐĂNG KÝ HANDLERS ===
def register_handlers(app: Application):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("xem_ghi_nho", xem_ghi_nho))
    app.add_handler(CommandHandler("xoa_ghi_nho_all", xoa_ghi_nho_all))
    app.add_handler(CommandHandler("tim_ghi_nho", tim_ghi_nho))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

