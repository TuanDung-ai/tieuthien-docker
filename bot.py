# bot.py
import os
import sys
import asyncio # Import asyncio
from flask import Flask, request, abort
from telegram import Update
from telegram.ext import ApplicationBuilder, Application # Import Application for type hinting

# === TOKEN từ biến môi trường ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8080)) # Cổng mà Flask sẽ lắng nghe

# Zeabur cung cấp URL công khai của dịch vụ.
# Biến môi trường này cần được thiết lập trên Zeabur dashboard (ví dụ: ZEABUR_URL)
ZEABUR_PUBLIC_URL = os.getenv("ZEABUR_URL") # Đây là biến môi trường phổ biến trên Zeabur
if not ZEABUR_PUBLIC_URL:
    print("WARNING: Biến môi trường ZEABUR_URL không tìm thấy. Vui lòng thiết lập trên Zeabur dashboard.", file=sys.stderr)
    # Fallback cho việc chạy cục bộ (ví dụ: dùng ngrok để tạo tunnel)
    ZEABUR_PUBLIC_URL = f"http://localhost:{PORT}" # Chỉ dùng cho test cục bộ, không dùng cho production

WEBHOOK_PATH = "/telegram-webhook" # Đường dẫn webhook mà Telegram sẽ gửi cập nhật đến
WEBHOOK_URL = f"{ZEABUR_PUBLIC_URL}{WEBHOOK_PATH}" # URL đầy đủ của webhook

# === IMPORT các hàm ===
try:
    from modules.handlers import register_handlers
    from memory.sync_on_startup import ensure_sqlite_cache
    from memory.sync_to_cloud import sync_sqlite_to_supabase
    print("DEBUG: Import các module thành công.")
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
    if not telegram_app:
        print("LỖI: Telegram Application instance chưa được khởi tạo.", file=sys.stderr)
        abort(500) # Lỗi Server nội bộ

    # Lấy cập nhật từ body của request
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    
    # Xử lý cập nhật bằng đối tượng application
    await telegram_app.process_update(update)
    return "ok" # Trả về 'ok' để Telegram biết cập nhật đã được nhận

# Hàm bất đồng bộ để thiết lập webhook (cần chạy trong một event loop)
async def set_telegram_webhook_async():
    print("DEBUG: Initializing Telegram Application...", file=sys.stderr)
    await telegram_app.initialize() # Khởi tạo Application
    print("DEBUG: Telegram Application initialized.", file=sys.stderr)

    print(f"DEBUG: Đặt webhook cho bot Telegram tại URL: {WEBHOOK_URL}", file=sys.stderr)
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)
    print("DEBUG: Đặt webhook thành công.", file=sys.stderr)

    print("DEBUG: Starting Telegram Application (for webhook processing)...", file=sys.stderr)
    await telegram_app.start() # Khởi động Application để xử lý cập nhật
    print("DEBUG: Telegram Application started.", file=sys.stderr)

# === KHỞI ĐỘNG ỨNG DỤNG ===
if __name__ == '__main__':
    print("DEBUG: Bắt đầu quá trình khởi động ứng dụng chính...")
    try:
        # Khởi tạo đối tượng Telegram Application
        telegram_app = ApplicationBuilder().token(TOKEN).build()
        register_handlers(telegram_app) # Đăng ký các handler

        # === Đồng bộ Supabase → SQLite ===
        print("DEBUG: Bắt đầu đồng bộ Supabase → SQLite...")
        ensure_sqlite_cache()
        print("DEBUG: Đồng bộ Supabase → SQLite hoàn tất.")

        # === Đồng bộ SQLite → Supabase ===
        print("DEBUG: Bắt đầu đồng bộ SQLite → Supabase...")
        sync_sqlite_to_supabase()
        print("DEBUG: Đồng bộ SQLite → Supabase hoàn tất.")

        # Thiết lập webhook một cách bất đồng bộ
        try:
            # Chạy hàm async trong main thread.
            # asyncio.run() sẽ tạo và quản lý event loop cần thiết.
            asyncio.run(set_telegram_webhook_async())
        except RuntimeError as e:
            # Xử lý trường hợp đã có event loop đang chạy (ít khả năng xảy ra trong ngữ cảnh này)
            if "cannot run an event loop while another loop is running" in str(e):
                print("WARNING: Có thể đã có một event loop đang chạy, thử sử dụng loop hiện có để thiết lập webhook.", file=sys.stderr)
                loop = asyncio.get_event_loop()
                loop.run_until_complete(set_telegram_webhook_async())
            else:
                raise e

        # Khởi động Flask web app trong luồng chính (blocking)
        # Flask sẽ lắng nghe trên cổng và nhận các yêu cầu webhook từ Telegram
        print(f"DEBUG: Bắt đầu Flask web server trên cổng {PORT}...")
        web_app.run(host="0.0.0.0", port=PORT)
        print("DEBUG: Flask web server đã dừng (có thể do lỗi hoặc shutdown).")

    except Exception as e:
        print(f"LỖI NGHIÊM TRỌNG khi khởi động ứng dụng chính: {e}", file=sys.stderr)
        sys.exit(1)
