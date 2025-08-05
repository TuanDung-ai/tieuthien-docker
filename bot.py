# bot.py
import os
import sys
import asyncio
import httpx
from fastapi import FastAPI, Request, Response

from telegram import Update
from telegram.ext import Application, ApplicationBuilder

# === Cấu hình từ biến môi trường ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("LỖI NGHIÊM TRỌNG: Biến môi trường TELEGRAM_BOT_TOKEN không được thiết lập.", file=sys.stderr)
    sys.exit(1)

PORT = int(os.getenv("PORT", 8080))
ZEABUR_PUBLIC_URL = os.getenv("ZEABUR_URL")
WEBHOOK_PATH = "/telegram-webhook"
WEBHOOK_URL = f"{ZEABUR_PUBLIC_URL}{WEBHOOK_PATH}" if ZEABUR_PUBLIC_URL else None

# === IMPORT các hàm ===
try:
    from modules.handlers import register_handlers
    from memory.sync_on_startup import ensure_sqlite_cache
    from memory.sync_to_cloud import sync_sqlite_to_supabase
    print("DEBUG: Import các module thành công.", file=sys.stderr)
except ImportError as e:
    print(f"LỖI KHỞI ĐỘNG: Không thể import module: {e}", file=sys.stderr)
    sys.exit(1)

# === Khởi tạo ứng dụng FastAPI và Telegram Application ===
# Sử dụng FastAPI thay vì Flask
app = FastAPI(docs_url=None, redoc_url=None) # Tắt docs tự động cho an toàn

# Tạo một instance duy nhất cho Application
# Instance này sẽ được chia sẻ an toàn trong môi trường ASGI
telegram_app: Application = ApplicationBuilder().token(TOKEN).build()


@app.on_event("startup")
async def startup_event():
    """
    Hàm này chạy một lần duy nhất khi ứng dụng ASGI khởi động.
    Đây là nơi lý tưởng để thực hiện các tác vụ cài đặt.
    """
    print("DEBUG: Bắt đầu quá trình khởi động ứng dụng (startup_event)...", file=sys.stderr)
    try:
        # 1. Đồng bộ dữ liệu từ cloud về local
        print("DEBUG: Bắt đầu đồng bộ Supabase → SQLite...", file=sys.stderr)
        ensure_sqlite_cache()
        print("DEBUG: Đồng bộ Supabase → SQLite hoàn tất.", file=sys.stderr)

        # 2. Đồng bộ dữ liệu từ local lên cloud (nếu cần)
        print("DEBUG: Bắt đầu đồng bộ SQLite → Supabase...", file=sys.stderr)
        sync_sqlite_to_supabase()
        print("DEBUG: Đồng bộ SQLite → Supabase hoàn tất.", file=sys.stderr)

        # 3. Đăng ký các handlers cho bot
        register_handlers(telegram_app)
        print("DEBUG: Đăng ký các handlers thành công.", file=sys.stderr)

        # 4. Khởi tạo Application (quan trọng!)
        await telegram_app.initialize()
        print("DEBUG: Telegram Application đã được initialize.", file=sys.stderr)

        # 5. Thiết lập Webhook
        # Mã này chỉ nên chạy khi deploy, không chạy ở local
        if ZEABUR_PUBLIC_URL:
            print(f"DEBUG: Thiết lập webhook tới URL: {WEBHOOK_URL}", file=sys.stderr)
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}&drop_pending_updates=True")
                if response.status_code == 200 and response.json().get("ok"):
                    print("DEBUG: Webhook đã được thiết lập thành công!", file=sys.stderr)
                else:
                    print(f"LỖI: Không thể thiết lập webhook. Phản hồi từ Telegram: {response.text}", file=sys.stderr)
        else:
             print("INFO: ZEABUR_URL không được thiết lập, bỏ qua việc cài đặt webhook. Bot sẽ chạy ở chế độ polling nếu được khởi động trực tiếp.", file=sys.stderr)


    except Exception as e:
        print(f"LỖI NGHIÊM TRỌNG trong quá trình startup: {e}", file=sys.stderr)
        # Tùy chọn: có thể muốn thoát ứng dụng ở đây nếu startup thất bại
        # sys.exit(1)

@app.on_event("shutdown")
async def shutdown_event():
    """Hàm này chạy khi ứng dụng tắt."""
    print("DEBUG: Bắt đầu quá trình shutdown...", file=sys.stderr)
    await telegram_app.shutdown()
    print("DEBUG: Telegram Application đã được shutdown.", file=sys.stderr)


# === Các Endpoints của Web App ===

@app.get("/")
@app.get("/health")
def health_check():
    """Endpoint để kiểm tra tình trạng hoạt động."""
    return {"status": "ok", "message": "✅ Tiểu Thiên đang vận hành bình thường."}


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """Endpoint nhận các cập nhật từ Telegram."""
    try:
        # Lấy dữ liệu JSON từ request
        json_data = await request.json()
        print(f"DEBUG: Dữ liệu JSON từ webhook: {json_data}", file=sys.stderr)
        
        # Tạo đối tượng Update
        update = Update.de_json(json_data, telegram_app.bot)
        
        # Xử lý update
        # process_update sẽ chạy các handler tương ứng một cách bất đồng bộ
        # mà không làm block hay đóng event loop.
        await telegram_app.process_update(update)
        print(f"DEBUG: Đã xử lý thành công update_id: {update.update_id}", file=sys.stderr)

        # Trả về 200 OK cho Telegram
        return Response(status_code=200)

    except Exception as e:
        print(f"LỖI trong telegram_webhook: {e}", file=sys.stderr)
        return Response(status_code=500)


# === Chạy cục bộ để test (sử dụng uvicorn) ===
if __name__ == '__main__':
    print("DEBUG: Chạy cục bộ bằng uvicorn...", file=sys.stderr)
    import uvicorn
    # Khi chạy local, ZEABUR_URL không có, bot sẽ không set webhook
    # Bạn có thể chạy bot ở chế độ polling để test
    # asyncio.run(telegram_app.run_polling())
    # Hoặc dùng ngrok để tạo URL public và set biến môi trường ZEABUR_URL để test webhook
    uvicorn.run(app, host="0.0.0.0", port=PORT)
