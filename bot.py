import os
import requests
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# 🔐 Lấy token & API key từ biến môi trường
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# 📁 File ghi nhớ
MEMORY_FILE = "memory.json"

# 🧠 Trạng thái người dùng (đang ghi nhớ hay không)
user_states = {}  # key: user_id, value: "waiting_note" hoặc None

# 📌 Hàm lưu ghi nhớ
def save_memory(user_id, content):
    data = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)

    user_key = str(user_id)
    if user_key not in data:
        data[user_key] = []

    memory_item = {
        "content": content,
        "time": datetime.now().isoformat()
    }

    data[user_key].append(memory_item)

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# 🤖 Hàm phản hồi AI qua OpenRouter (Thiên Cơ phong cách)
def get_ai_response(user_prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
            "content": (
                "Bạn là Thiên Cơ – một AI trợ lý cá nhân đáng tin cậy. "
                "Giọng điệu trầm ổn, chính xác, nhẹ nhàng, thỉnh thoảng có chút hài hước nhẹ. "
                "Luôn trả lời ngắn gọn, không quá 3 câu. Cuối mỗi phản hồi, đưa ra gợi ý tiếp theo phù hợp. "
                "Ví dụ: 'Bạn cần ghi nhớ điều gì?', 'Thiên Cơ có thể nhắc lịch, tâm sự hoặc kể chuyện...'. "
                "Nếu không rõ câu hỏi, hãy hỏi lại nhẹ nhàng. Không trả lời quá dài hay lan man."
            )
        },
        {
            "role": "user",
            "content": user_prompt
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
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print("Lỗi AI:", e)
        return "Thiên Cơ gặp trục trặc nhẹ... thử lại sau nhé."

# /start – khởi đầu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Chào người dùng, bạn muốn Thiên Cơ giúp gì hôm nay?"
    ai_reply = get_ai_response(prompt)

    keyboard = [
        [
            InlineKeyboardButton("📝 Ghi nhớ", callback_data='note'),
            InlineKeyboardButton("📅 Lịch", callback_data='calendar'),
            InlineKeyboardButton("🎧 Thư giãn", callback_data='relax')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(ai_reply, reply_markup=reply_markup)

# /help – hướng dẫn
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🌀 Thiên Cơ lắng nghe...\n\n"
        "Lệnh khả dụng:\n"
        "/start – Bắt đầu trò chuyện\n"
        "/help – Danh sách lệnh\n"
        "(Hoặc chat bất kỳ để nhận phản hồi từ Thiên Cơ)"
    )
    await update.message.reply_text(msg)

# Xử lý tin nhắn văn bản
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    if user_states.get(user_id) == "waiting_note":
        save_memory(user_id, user_text)
        user_states[user_id] = None
        await update.message.reply_text("📌 Thiên Cơ đã ghi nhớ điều bạn vừa nói.")
    else:
        ai_reply = get_ai_response(user_text)
        keyboard = [
            [
                InlineKeyboardButton("📝 Ghi nhớ", callback_data='note'),
                InlineKeyboardButton("📅 Lịch", callback_data='calendar'),
                InlineKeyboardButton("🎧 Thư giãn", callback_data='relax')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(ai_reply, reply_markup=reply_markup)

# Xử lý khi bấm nút
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    choice = query.data

    if choice == 'note':
        user_states[user_id] = "waiting_note"
        await query.edit_message_text("📝 Bạn muốn ghi nhớ điều gì? Gõ nội dung vào nhé.")
    elif choice == 'calendar':
        await query.edit_message_text("📅 Chức năng lịch chưa mở, đang cập nhật.")
    elif choice == 'relax':
        await query.edit_message_text("🎧 Mời bạn hít thở sâu... Thiên Cơ sẽ kể chuyện hoặc phát nhạc nhẹ nhàng.")

# Khởi chạy bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("🤖 Bot Thiên Cơ đang hoạt động...")
    app.run_polling()
