# bot.py
import os
import sys
import asyncio # Vẫn cần nếu có các hàm async khác trong handlers
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, Application

# === TOKEN từ biến môi trường ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080))

# Zeabur cung cấp URL công khai của dịch vụ.
ZEABUR_PUBLIC_URL = os.getenv("ZEABUR_URL")
if not ZEABUR_PUBLIC_URL:
    print("WARNING: Biến môi trường ZEABUR_URL không tìm thấy. Vui lòng thiết lập trên Zeabur dashboard.", file=sys.stderr)
    ZEABUR_PUBLIC_URL = f"http://localhost:{PORT}" # Fallback cho local testing

WEBHOOK_PATH = "/telegram-webhook"
WEBHOOK_URL = f"{ZEABUR_PUBLIC_URL}{WEBHOOK_PATH}"

# === IMPORT các hàm ===
try:
    from modules.handlers import register_handlers
    from memory.sync_on_startup import ensure_sqlite_cache
    from memory.sync_to_cloud import sync_sqlite_to_supabase
    print("DEBUG: Import các module thành công.", file=sys.stderr)
except ImportError as e:
    print(f"LỖI KHỞI ĐỘNG: Không thể import module: {e}", file=sys.stderr)
    sys.exit(1)

# Biến toàn cục cho đối tượng Telegram Application
telegram_app: Application = None

# === Web health check ===
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health_check():
    return "✅ Tiểu Thiên đang vận hành bình thường."

# Webhook endpoint cho Telegram
@web_app.route(WEBHOOK_PATH, methods=['POST'])
async def telegram_webhook():
    print("DEBUG: Webhook nhận được yêu cầu POST!", file=sys.stderr)
    if not telegram_app:
        print("LỖI: Telegram Application instance chưa được khởi tạo.", file=sys.stderr)
        abort(500)

    try:
        json_data = request.get_json(force=True)
        print(f"DEBUG: Dữ liệu JSON từ webhook: {json_data}", file=sys.stderr)
        update = Update.de_json(json_data, telegram_app.bot)
        
        print(f"DEBUG: Update nhận được: {update.update_id}, từ người dùng: {update.effective_user.id}", file=sys.stderr)
        await telegram_app.process_update(update)
        print("DEBUG: process_update đã được gọi.", file=sys.stderr)
        return "ok"
    except Exception as e:
        print(f"LỖI trong telegram_webhook: {e}", file=sys.stderr)
        return "error", 500

# Hàm bất đồng bộ để thiết lập webhook (chỉ đặt webhook)
async def setup_telegram_webhook_only():
    print(f"DEBUG: Đặt webhook cho bot Telegram tại URL: {WEBHOOK_URL}", file=sys.stderr)
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    print("DEBUG: Đặt webhook thành công.", file=sys.stderr)

# === KHỞI ĐỘNG ỨNG DỤNG (LOGIC CHẠY KHI MODULE ĐƯỢC IMPORT BỞI GUNICORN) ===
# Tất cả logic khởi tạo cần được đặt ở đây, ngoài khối if __name__ == '__main__':
print("DEBUG: Bắt đầu quá trình khởi động ứng dụng chính (Gunicorn context)...", file=sys.stderr)
try:
    # Khởi tạo đối tượng Telegram Application
    telegram_app = ApplicationBuilder().token(TOKEN).build()
    register_handlers(telegram_app) # Đăng ký các handler

    # === Đồng bộ Supabase → SQLite ===
    print("DEBUG: Bắt đầu đồng bộ Supabase → SQLite...", file=sys.stderr)
    ensure_sqlite_cache()
    print("DEBUG: Đồng bộ Supabase → SQLite hoàn tất.", file=sys.stderr)

    # === Đồng bộ SQLite → Supabase ===
    print("DEBUG: Bắt đầu đồng bộ SQLite → Supabase...", file=sys.stderr)
    sync_sqlite_to_supabase()
    print("DEBUG: Đồng bộ SQLite → Supabase hoàn tất.", file=sys.stderr)

    # KHÔNG CÒN GỌI setup_telegram_webhook_only() Ở ĐÂY NỮA
    print("DEBUG: Ứng dụng đã sẵn sàng. Gunicorn sẽ khởi chạy web server.", file=sys.stderr)

except Exception as e:
    print(f"LỖI NGHIÊM TRỌNG khi khởi động ứng dụng chính: {e}", file=sys.stderr)
    sys.exit(1)

# The if __name__ == '__main__': block is now empty or used for local testing only
if __name__ == '__main__':
    print("DEBUG: Chạy cục bộ (không dùng Gunicorn).", file=sys.stderr)
    # This block is for local development without Gunicorn
    # web_app.run(host="0.0.0.0", port=PORT) # Uncomment for local Flask dev server
