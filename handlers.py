import os
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sheets import (
    save_memory, get_memory, search_memory,
    clear_memory, delete_memory_item, update_latest_memory_type,
    get_recent_memories_for_prompt
)

# === API KEY OpenRouter ===
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
user_states = {}  # user_id -> trạng thái hoặc dict

# === GIAO DIỆN NÚT ===
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Ghi nhớ", callback_data='note'),
            InlineKeyboardButton("📅 Lịch", callback_data='calendar'),
            InlineKeyboardButton("🎷 Thư giãn", callback_data='relax')
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
    lines = text.strip().split('\n')
    short_text = " ".join(line.strip() for line in lines if line.strip())
    if len(short_text) > 500:
        short_text = short_text[:497] + "..."
    footer = "\n\n💡 Bạn cần gì tiếp theo? Ví dụ: '📝 Ghi nhớ', '📅 Lịch', '🎷 Thư giãn'."
    return f"🧐 Thiên Cơ:\n\n{short_text}{footer}"

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
            memory_context = f"Người dùng trước đó đã ghi nhớ:\n{mems}\n\n"
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

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Chào người dùng, bạn muốn Thiên Cơ giúp gì hôm nay?"
    ai_reply = get_ai_response(prompt, user_id=update.message.from_user.id)
    await update.message.reply_text(ai_reply, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🌀 Thiên Cơ lắng nghe...\n\n"
        "Lệnh khả dụng:\n"
        "/start – Bắt đầu trò chuyện\n"
        "/help – Danh sách lệnh\n"
        "/xem_ghi_nho – Xem lại ký ức\n"
        "/xoa_ghi_nho_all – Xóa toàn bộ ghi nhớ\n"
        "/tim_ghi_nho <từ khóa> – Tìm ghi nhớ\n"
        "(Hoặc chat bất kỳ để trò chuyện cùng Thiên Cơ)"
    )
    await update.message.reply_text(msg)

# === Hàm khác được cập nhật tiếp ===
# (xem_ghi_nho, xoa_ghi_nho_all, tim_ghi_nho, handle_message, button_callback)
# Thiên Cơ sẽ thêm tiếp phần còn lại ngay nếu bạn xác nhận tạo file sheets.py!
