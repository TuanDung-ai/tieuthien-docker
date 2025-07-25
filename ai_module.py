import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Lấy token từ biến môi trường
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# Hàm phản hồi AI qua OpenRouter (Thiên Cơ phong cách cá nhân hóa)
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

# Lệnh /start – mở đầu cuộc trò chuyện
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

# Lệnh /help – hiển thị hướng dẫn
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🌀 Thiên Cơ lắng nghe...\n\n"
        "Lệnh khả dụng:\n"
        "/start – Bắt đầu trò chuyện\n"
        "/help – Danh sách lệnh\n"
        "(Hoặc chat bất kỳ để nhận phản hồi từ Thiên Cơ)"
    )
    await update.message.reply_text(msg)

# Phản hồi mọi tin nhắn văn bản
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
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

# Xử lý khi người dùng bấm nút
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    if choice == 'note':
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
