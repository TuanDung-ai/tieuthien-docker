# handlers/commands.py
from telegram import Update
from telegram.ext import ContextTypes
from modules.memory_manager import save_memory, get_memory, delete_single_memory, clear_memory
from modules.buttons import get_main_keyboard


async def cmd_ghi_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    content = ' '.join(context.args)
    if not content:
        await update.message.reply_text("⚠️ Bạn cần nhập nội dung để ghi nhớ.")
        return
    save_memory(user_id, content)
    await update.message.reply_text("✅ Đã ghi nhớ.")


async def cmd_xem_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    memories = get_memory(user_id)
    if not memories:
        await update.message.reply_text("📭 Bạn chưa có ghi nhớ nào.")
        return

    reply = "📖 Ghi nhớ gần nhất:\n\n"
    for mem in memories[-5:]:
        reply += f"📝 ID {mem.get('id')}: ({mem.get('note_type', 'khác')}) {mem.get('content', '')}\n"

    await update.message.reply_text(reply)


async def cmd_xoa_nho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Bạn cần cung cấp ID để xoá ghi nhớ.")
        return

    try:
        note_id = int(context.args[0])
        delete_single_memory(user_id, note_id)
        await update.message.reply_text(f"🗑️ Đã xoá ghi nhớ ID {note_id}.")
    except ValueError:
        await update.message.reply_text("❌ ID phải là số.")


async def cmd_xoa_tatca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    clear_memory(user_id)
    await update.message.reply_text("🧹 Đã xoá toàn bộ ghi nhớ.")


async def cmd_tro_giup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Tôi là Thiên Cơ – trợ lý AI cá nhân.\n\n"
        "Các lệnh có thể dùng:\n"
        "/ghi_nho <nội dung> – Lưu ghi nhớ\n"
        "/xem_nho – Xem 5 ghi nhớ gần nhất\n"
        "/xoa_nho <id> – Xoá ghi nhớ theo ID\n"
        "/xoa_tatca – Xoá toàn bộ ghi nhớ\n"
        "/tro_giup – Hiển thị hướng dẫn",
        reply_markup=get_main_keyboard()
    )
