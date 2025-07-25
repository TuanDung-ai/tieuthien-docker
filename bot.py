import os
import json
import requests
from datetime import datetime
from flask import Flask
import threading

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# === TOKEN và API KEY ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# === FILE LƯU NHỚ ===
MEMORY_FILE = "memory.json"
user_states = {}  # user_id → trạng thái hoặc dict khi tìm kiếm

# === HÀM GHI NHỚ PHÂN LOẠI ===
def save_memory(user_id, content, note_type="khác"):
    data = {}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
        except Exception as e:
            print("Lỗi đọc file ghi nhớ:", e)
            data = {}

    user_key = str(user_id)
    if user_key not in data:
        data[user_key] = []

    memory_item = {
        "content": content,
        "type": note_type,
        "time": datetime.now().isoformat()
    }

    data[user_key].append(memory_item)

    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === LẤY GHI NHỚ (lọc loại nếu cần) ===
def get_memory(user_id, note_type=None):
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
        all_notes = data.get(str(user_id), [])
        if note_type:
            return [note for note in all_notes if note["type"] == note_type]
        return all_notes
    except Exception as e:
        print("Lỗi đọc file ghi nhớ:", e)
        return []

# === TÌM KIẾM GHI NHỚ ===
def search_memory(user_id, keyword):
    notes = get_memory(user_id)
    result = []
    keyword_lower = keyword.lower()
    for idx, note in enumerate(notes):
        if (keyword_lower in note["content"].lower()) or (keyword_lower in note["type"].lower()):
            result.append((idx, note))
    return result

# === XÓA GHI NHỚ ===
def clear_memory(user_id):
    if not os.path.exists(MEMORY_FILE):
        return False
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        print("Lỗi đọc file ghi nhớ:", e)
        return False
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
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        print("Lỗi đọc file ghi nhớ:", e)
        return False
    user_key = str(user_id)
    if user_key in data and 0 <= index < len(data[user_key]):
        del data[user_key][index]
        if not data[user_key]:
            del data[user_key]
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    return False

# === CẬP NHẬT PHÂN LOẠI CHO GHI NHỚ MỚI NHẤT ===
def update_latest_memory_type(user_id, note_type):
    if not os.path.exists(MEMORY_FILE):
        return False
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
        user_key = str(user_id)
        if user_key in data and data[user_key]:
            data[user_key][-1]["type"] = note_type
            with open(MEMORY_FILE, "w") as f:
                json.dump(data, f, indent=2)
            return True
    except Exception as e:
        print("Lỗi cập nhật loại ghi nhớ:", e)
    return False

# === TRA CỨU GHI NHỚ GẦN NHẤT ===
def get_recent_memories_for_prompt(user_id, limit=3):
    notes = get_memory(user_id)
    notes.sort(key=lambda x: x["time"], reverse=True)
    recent = notes[:limit]
    return "\n".join(f"- ({n['type']}) {n['content']}" for n in recent)

# === HÀM ĐỊNH DẠNG PHẢN HỒI AI ===
def format_ai_response(text):
    lines = text.strip().split('\n')
    short_text = " ".join(line.strip() for line in lines if line.strip())
    if len(short_text) > 500:
        short_text = short_text[:497] + "..."
    footer = "\n\n\ud83d\udca1 Bạn cần gì tiếp theo? Ví dụ: '\ud83d\udcdd Ghi nhớ', '\ud83d\udcc5 Lịch', '\ud83c\udfb7 Thư giãn'."
    return f"\ud83e\udd16 Thiên Cơ:\n\n{short_text}{footer}"

# === PHẢN HỒI AI (có chèn ghi nhớ) ===
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
        return "\u26a0\ufe0f Thiên Cơ gặp trục trặc nhẹ... thử lại sau nhé."

# === LỆNH TÌM KIẾM ===
async def tim_ghi_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args:
        await update.message.reply_text("\ud83d\udd0d Vui lòng gõ từ khóa sau lệnh. Ví dụ: /tim_ghi_nho nhắc nhở")
        return

    keyword = " ".join(context.args)
    results = search_memory(user_id, keyword)

    if not results:
        await update.message.reply_text(f"\ud83d\udcdd Không tìm thấy ghi nhớ nào chứa: '{keyword}'.")
    else:
        msg = f"\ud83d\udd0d Kết quả tìm kiếm: '{keyword}'\n\n"
        for idx, (real_index, item) in enumerate(results, start=1):
            content = item["content"]
            note_type = item.get("type", "khác")
            time_str = item["time"].split("T")[0]
            msg += f"{idx}. ({note_type}) {content} ({time_str})\n"
        msg += "\nGõ số để xóa ghi nhớ tương ứng hoặc /xoa_ghi_nho_all để xóa hết."
        user_states[user_id] = {"state": "waiting_delete_search", "map": [i[0] for i in results]}
        await update.message.reply_text(msg)

# === FLASK SERVER CHO UPTIMEROBOT ===
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health_check():
    return "\u2705 Tiểu Thiên đang vận hành bình thường."

def run_web_app():
    web_app.run(host="0.0.0.0", port=8080)

# === KHỞI CHẠY BOT & FLASK SONG SONG ===
if __name__ == '__main__':
    threading.Thread(target=run_web_app).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("xem_ghi_nho", xem_ghi_nho))
    app.add_handler(CommandHandler("xoa_ghi_nho_all", xoa_ghi_nho_all))
    app.add_handler(CommandHandler("tim_ghi_nho", tim_ghi_nho))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("\ud83e\udd16 Bot Thiên Cơ đã hồi sinh và vận hành...")
    app.run_polling()
