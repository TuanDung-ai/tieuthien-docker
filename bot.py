# bot.py
import os
import sys
import asyncio
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

# KHÔNG DÙNG biến toàn cục telegram_app ở đây nữa
# Mỗi worker sẽ có instance riêng

# === Web health check ===
web_app = Flask(__name__)

@web_app.route('/')
@web_app.route('/health')
def health_check():
    return "✅ Tiểu Thiên đang vận hành bình thường."

# Hàm để lấy hoặc khởi tạo đối tượng Telegram Application cho mỗi worker
# Hàm này giờ là async vì nó gọi app_instance.initialize()
async def get_telegram_app() -> Application:
    # Sử dụng một thuộc tính trên đối tượng Flask app để lưu trữ instance của telegram_app
    # Điều này đảm bảo mỗi worker có một instance riêng biệt
    if not hasattr(web_app, 'telegram_app_instance'):
        print("DEBUG: Khởi tạo Telegram Application cho worker...", file=sys.stderr)
        app_instance = ApplicationBuilder().token(TOKEN).build()
        register_handlers(app_instance)
        # KHÔNG GỌI app_instance.initialize() NỮA KHI DÙNG WEBHOOK VỚI FLASK/GUNICORN
        # Flask/Gunicorn đã quản lý event loop, và initialize() có thể gây xung đột.
        setattr(web_app, 'telegram_app_instance', app_instance)
        print("DEBUG: Telegram Application khởi tạo thành công cho worker.", file=sys.stderr)
    return web_app.telegram_app_instance

# Webhook endpoint cho Telegram
@web_app.route(WEBHOOK_PATH, methods=['POST'])
async def telegram_webhook():
    print("DEBUG: Webhook nhận được yêu cầu POST!", file=sys.stderr)
    
    # Lấy instance telegram_app cho worker hiện tại (giờ là awaitable)
    current_telegram_app = await get_telegram_app()

    try:
        json_data = request.get_json(force=True)
        print(f"DEBUG: Dữ liệu JSON từ webhook: {json_data}", file=sys.stderr)
        update = Update.de_json(json_data, current_telegram_app.bot)
        
        print(f"DEBUG: Update nhận được: {update.update_id}, từ người dùng: {update.effective_user.id}", file=sys.stderr)
        await current_telegram_app.process_update(update)
        print("DEBUG: process_update đã được gọi.", file=sys.stderr)
        return "ok"
    except Exception as e:
        print(f"LỖI trong telegram_webhook: {e}", file=sys.stderr)
        return "error", 500

# === KHỞI ĐỘNG ỨNG DỤNG (LOGIC CHẠY KHI MODULE ĐƯỢC IMPORT BỞI GUNICORN) ===
# Các logic đồng bộ Supabase vẫn giữ nguyên ở đây
print("DEBUG: Bắt đầu quá trình khởi động ứng dụng chính (Gunicorn context)...", file=sys.stderr)
try:
    # === Đồng bộ Supabase → SQLite ===
    print("DEBUG: Bắt đầu đồng bộ Supabase → SQLite...", file=sys.stderr)
    ensure_sqlite_cache()
    print("DEBUG: Đồng bộ Supabase → SQLite hoàn tất.", file=sys.stderr)

    # === Đồng bộ SQLite → Supabase ===
    print("DEBUG: Bắt đầu đồng bộ SQLite → Supabase...", file=sys.stderr)
    sync_sqlite_to_supabase()
    print("DEBUG: Đồng bộ SQLite → Supabase hoàn tất.", file=sys.stderr)

    # KHÔNG CÒN initialize() hay start() ở đây nữa
    # Việc khởi tạo telegram_app sẽ diễn ra trong get_telegram_app() cho mỗi worker
    # Việc đặt webhook đã được xử lý bởi deploy_setup.py

    print("DEBUG: Ứng dụng đã sẵn sàng. Gunicorn sẽ khởi chạy web server.", file=sys.stderr)

except Exception as e:
    print(f"LỖI NGHIÊM TRỌNG khi khởi động ứng dụng chính: {e}", file=sys.stderr)
    sys.exit(1)

# The if __name__ == '__main__': block is now empty or used for local testing only
if __name__ == '__main__':
    print("DEBUG: Chạy cục bộ (không dùng Gunicorn).", file=sys.stderr)
    # This block is for local development without Gunicorn
    # web_app.run(host="0.0.0.0", port=PORT) # Uncomment for local Flask dev server
