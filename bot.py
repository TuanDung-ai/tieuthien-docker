import os
import json
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# === TOKEN và API KEY ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# === FILE LƯU NHỚ ===
MEMORY_FILE = "memory.json"
user_states = {}  # user_id → trạng thái: None / waiting_note / waiting_delete

# === HÀM GHI NHỚ ===
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

def get_memory(user_id):
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    return data.get(str(user_id), [])

def clear_memory(user_id):
    if not os.path.exists(MEMORY_FILE):
        return False
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    user_key = str(user_id)
    if user_key in data:
        del data[user_key]
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    return False

def delete_memory_item(user_id, index):
    if not os.path.exists(MEMORY_FILE):
        return False
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    user_key = str(user_id)
    if user_key in data and 0 <= index < len(data[user_key]):
        del data[user_key][index]
        if not data[user_key]:
            del data[user_key]
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    return False

# === PHẢN HỒI AI ===
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

# === GIAO DIỆN NÚT ===
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📝 Ghi nhớ", callback_data='note'),
            InlineKeyboardButton("📅 Lịch", callback_data='calendar'),
            InlineKeyboardButton("🎧 Thư giãn", callback_data='relax')
        ],
        [
            InlineKeyboardButton("📖 Xem nhớ", callback_data='view'),
            InlineKeyboardButton("🗑️ Xóa hết", callback_data='clear_all')
        ]
    ])

# === LỆNH /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = "Chào người dùng, bạn muốn Thiên Cơ giúp gì hôm nay?"
    ai_reply = get_ai_response(prompt)
    await update.message.reply_text(ai_reply, reply_markup=get_main_keyboard())

# === LỆNH /help ===
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🌀 Thiên Cơ lắng nghe...\n\n"
        "Lệnh khả dụng:\n"
        "/start – Bắt đầu trò chuyện\n"
        "/help – Danh sách lệnh\n"
        "/xem_ghi_nho – Xem lại ký ức\n"
        "/xoa_ghi_nho_all – Xóa toàn bộ ghi nhớ\n"
        "(Hoặc chat bất kỳ để trò chuyện cùng Thiên Cơ)"
    )
    await update.message.reply_text(msg)

# === /xem_ghi_nho ===
async def xem_ghi_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_id = update.message.from_user.id
        send = update.message.reply_text
    else:
        user_id = update.callback_query.from_user.id
        send = update.callback_query.edit_message_text

    memories = get_memory(user_id)

    if not memories:
        await send("📭 Bạn chưa ghi nhớ gì cả.")
    else:
        msg = "📖 Ghi nhớ của bạn:\n\n"
        for idx, item in enumerate(memories, start=1):
            content = item["content"]
            time_str = item["time"].split("T")[0]
            msg += f"{idx}. {content} ({time_str})\n"
        msg += "\nGõ số ghi nhớ cần xóa hoặc /xoa_ghi_nho_all để xóa hết."
        user_states[user_id] = "waiting_delete"
        await send(msg)

# === /xoa_ghi_nho_all ===
async def xoa_ghi_nho_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_id = update.message.from_user.id
        send = update.message.reply_text
    else:
        user_id = update.callback_query.from_user.id
        send = update.callback_query.edit_message_text

    success = clear_memory(user_id)
    user_states[user_id] = None

    if success:
        await send("🗑️ Thiên Cơ đã xóa toàn bộ ghi nhớ của bạn.")
    else:
        await send("📭 Không có gì để xóa cả.")

# === XỬ LÝ TIN NHẮN ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text.strip()
    state = user_states.get(user_id)

    if state == "waiting_note":
        save_memory(user_id, user_text)
        user_states[user_id] = None
        await update.message.reply_text("📌 Thiên Cơ đã ghi nhớ điều bạn vừa nói.")
    elif state == "waiting_delete":
        if user_text.isdigit():
            index = int(user_text) - 1
            success = delete_memory_item(user_id, index)
            if success:
                await update.message.reply_text(f"🗑️ Đã xóa ghi nhớ số {user_text}.")
            else:
                await update.message.reply_text("❗ Số không hợp lệ. Thử lại.")
            user_states[user_id] = None
        else:
            await update.message.reply_text("❗ Vui lòng gõ số để xóa hoặc /xoa_ghi_nho_all.")
    else:
        ai_reply = get_ai_response(user_text)
        await update.message.reply_text(ai_reply, reply_markup=get_main_keyboard())

# === XỬ LÝ NÚT ===
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data

    if choice == 'note':
        await query.edit_message_text("📝 Bạn muốn ghi nhớ điều gì? Gõ nội dung vào nhé.")
        user_states[user_id] = "waiting_note"
    elif choice == 'calendar':
        await query.edit_message_text("📅 Chức năng lịch chưa mở, đang cập nhật.")
    elif choice == 'relax':
        await query.edit_message_text("🎧 Hít thở sâu... Thiên Cơ sẽ kể chuyện hoặc phát nhạc nhẹ nhàng.")
    elif choice == 'view':
        await xem_ghi_nho(update, context)
    elif choice == 'clear_all':
        await xoa_ghi_nho_all(update, context)

# === KHỞI CHẠY BOT ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("xem_ghi_nho", xem_ghi_nho))
    app.add_handler(CommandHandler("xoa_ghi_nho_all", xoa_ghi_nho_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("🤖 Bot Thiên Cơ đã hồi sinh và vận hành...")
    app.run_polling()
