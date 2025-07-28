import os
import json
import requests
from datetime import datetime
from flask import Flask
import threading
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# === CẤU HÌNH LOG ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === TOKEN và API KEY ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
ZEABUR_MEMORY_API = os.getenv("ZEABUR_MEMORY_API")

# === FILE LƯU NHỚ ===
MEMORY_FILE = "memory.json"
user_states = {}  # user_id → trạng thái hoặc dict khi tìm kiếm

# === HÀM XỬ LÝ FILE GHI NHỚ ===
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Lỗi đọc file ghi nhớ:", exc_info=True)
        return {}

def save_memory_to_file(data):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error("Lỗi ghi file ghi nhớ:", exc_info=True)

# === GHI NHỚ LÊN GOOGLE SHEETS ===
def save_memory(user_id, content, note_type="khác"):
    data = load_memory()
    user_key = str(user_id)
    if user_key not in data:
        data[user_key] = []

    memory_item = {
        "content": content,
        "type": note_type,
        "time": datetime.now().isoformat()
    }

    data[user_key].append(memory_item)
    save_memory_to_file(data)

    # Ghi thêm vào Google Sheets
    if ZEABUR_MEMORY_API:
        try:
            payload = {
                "chu_de": note_type,
                "noi_dung": content,
                "ghi_chu": f"From Telegram user {user_id}"
            }
            res = requests.post(f"{ZEABUR_MEMORY_API}/ghi_nho", json=payload, timeout=10)
            res.raise_for_status()
            logger.info("Ghi nhớ cloud thành công: %s", res.status_code)
        except Exception as e:
            logger.error("Lỗi ghi nhớ cloud:", exc_info=True)

# === LẤY GHI NHỚ ===
def get_memory(user_id, note_type=None):
    data = load_memory()
    all_notes = data.get(str(user_id), [])
    if note_type:
        return [note for note in all_notes if note["type"] == note_type]
    return all_notes

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
    data = load_memory()
    user_key = str(user_id)
    if user_key in data:
        del data[user_key]
        save_memory_to_file(data)
        return True
    return False

def delete_memory_item(user_id, index):
    data = load_memory()
    user_key = str(user_id)
    if user_key in data and 0 <= index < len(data[user_key]):
        del data[user_key][index]
        if not data[user_key]:
            del data[user_key]
        save_memory_to_file(data)
        return True
    return False

# === CẬP NHẬT PHÂN LOẠI ===
def update_latest_memory_type(user_id, note_type):
    data = load_memory()
    user_key = str(user_id)
    if user_key in data and data[user_key]:
        data[user_key][-1]["type"] = note_type
        save_memory_to_file(data)
        return True
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
    footer = "\n\n💡 Bạn cần gì tiếp theo? Ví dụ: '📝 Ghi nhớ', '📅 Lịch', '🎧 Thư giãn'."
    return f"🤖 Thiên Cơ:\n\n{short_text}{footer}"

# === PHẢN HỒI AI ===
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
        {"role": "system", "content": "Bạn là Thiên Cơ – AI trợ lý cá nhân đáng tin cậy. Luôn trả lời trầm ổn, chính xác, tối đa 3 câu, có thể sử dụng dữ kiện cũ."},
        {"role": "user", "content": memory_context + user_prompt}
    ]

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.6,
        "max_tokens": 400
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"]
        return format_ai_response(raw_text)
    except Exception as e:
        logger.error("Lỗi AI:", exc_info=True)
        return "⚠️ Thiên Cơ gặp trục trặc nhẹ... thử lại sau nhé."

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

# === HANDLER LỆNH ===
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

async def xem_ghi_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    memories = get_memory(user_id)
    if not memories:
        await update.message.reply_text("📭 Bạn chưa ghi nhớ gì cả.")
    else:
        msg = "📖 Ghi nhớ của bạn:\n\n"
        for idx, item in enumerate(memories, start=1):
            content = item["content"]
            note_type = item.get("type", "khác")
            time_str = item["time"].split("T")[0]
            msg += f"{idx}. ({note_type}) {content} ({time_str})\n"
        msg += "\nGõ số ghi nhớ cần xóa hoặc /xoa_ghi_nho_all để xóa hết."
        user_states[user_id] = "waiting_delete"
        await update.message.reply_text(msg)

async def xoa_ghi_nho_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    success = clear_memory(user_id)
    user_states[user_id] = None
    if success:
        await update.message.reply_text("🗑️ Thiên Cơ đã xóa toàn bộ ghi nhớ của bạn.")
    else:
        await update.message.reply_text("📭 Không có gì để xóa cả.")

async def tim_ghi_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args:
        await update.message.reply_text("🔍 Vui lòng gõ từ khóa sau lệnh. Ví dụ: /tim_ghi_nho nhắc nhở")
        return

    keyword = " ".join(context.args)
    results = search_memory(user_id, keyword)

    if not results:
        await update.message.reply_text(f"📝 Không tìm thấy ghi nhớ nào chứa: '{keyword}'.")
    else:
        msg = f"🔍 Kết quả tìm kiếm: '{keyword}'\n\n"
        for idx, (real_index, item) in enumerate(results, start=1):
            content = item["content"]
            note_type = item.get("type", "khác")
            time_str = item["time"].split("T")[0]
            msg += f"{idx}. ({note_type}) {content} ({time_str})\n"
        msg += "\nGõ số để xóa ghi nhớ tương ứng hoặc /xoa_ghi_nho_all để xóa hết."
        user_states[user_id] = {"state": "waiting_delete_search", "map": [i[0] for i in results]}
        await update.message.reply_text(msg)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text.strip()
    state = user_states.get(user_id)

    if state == "waiting_note":
        save_memory(user_id, user_text, note_type="khác")
        user_states[user_id] = "choosing_type"
        await update.message.reply_text(
            "📌 Thiên Cơ đã ghi nhớ. Chọn loại cho ghi nhớ này:",
            reply_markup=get_note_type_keyboard()
        )
    elif isinstance(state, dict) and state.get("state") == "waiting_delete_search":
        if user_text.isdigit():
            pos = int(user_text) - 1
            if 0 <= pos < len(state["map"]):
                real_index = state["map"][pos]
                success = delete_memory_item(user_id, real_index)
                if success:
                    await update.message.reply_text(f"🗑️ Đã xóa ghi nhớ số {user_text}.")
                else:
                    await update.message.reply_text("❗ Xóa thất bại. Thử lại.")
                user_states[user_id] = None
            else:
                await update.message.reply_text("❗ Số không hợp lệ. Thử lại.")
        else:
            await update.message.reply_text("❗ Vui lòng gõ số để xóa hoặc /xoa_ghi_nho_all.")
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
    elif state == "choosing_type":
        await update.message.reply_text("❗ Vui lòng chọn loại ghi nhớ từ nút bấm.")
    else:
        ai_reply = get_ai_response(user_text, user_id=user_id)
        await update.message.reply_text(ai_reply, reply_markup=get_main_keyboard())

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
        # Tạo giả Update và Context để gọi hàm xem_ghi_nho
        # Nhưng để đơn giản ta gọi luôn:
        user_states[user_id] = None
        memories = get_memory(user_id)
        if not memories:
            await query.edit_message_text("📭 Bạn chưa ghi nhớ gì cả.")
        else:
            msg = "📖 Ghi nhớ của bạn:\n\n"
            for idx, item in enumerate(memories, start=1):
                content = item["content"]
                note_type = item.get("type", "khác")
                time_str = item["time"].split("T")[0]
                msg += f"{idx}. ({note_type}) {content} ({time_str})\n"
            msg += "\nGõ số ghi nhớ cần xóa hoặc /xoa_ghi_nho_all để xóa hết."
            user_states[user_id] = "waiting_delete"
            await query.edit_message_text(msg)
    elif choice == 'clear_all':
        success = clear_memory(user_id)
        user_states[user_id] = None
        if success:
            await query.edit_message_text("🗑️ Thiên Cơ đã xóa toàn bộ ghi nhớ của bạn.")
        else:
            await query.edit_message_text("📭 Không có gì để xóa cả.")
    elif choice.startswith('type_'):
        type_map = {
            'type_tamsu': 'tâm sự',
            'type_nhacnho': 'nhắc nhở',
            'type_ytuong': 'ý tưởng',
            'type_canhan': 'cá nhân'
        }
        note_type = type_map.get(choice, 'khác')
        success = update_latest_memory_type(user_id, note_type)
        if success:
            await query.edit_message_text(f"📂 Ghi nhớ đã được phân loại: {note_type}.")
        else:
            await query.edit_message_text("⚠️ Không thể cập nhật loại ghi nhớ.")
        user_states[user_id] = None

# === FLASK SERVER ===
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health_check():
    return "✅ Tiểu Thiên đang vận hành bình thường."

async def run_web_app():
    web_app.run(host="0.0.0.0", port=8080)

# === KHỞI CHẠY BOT ===
if __name__ == '__main__':
    threading.Thread(target=web_app.run, kwargs={"host": "0.0.0.0", "port": 8080}).start()
    app = ApplicationBuilder().token(TOKEN).build()
    # Thêm handler...
    logger.info("🤖 Bot Thiên Cơ đã hồi sinh và vận hành...")
    app.run_polling()
