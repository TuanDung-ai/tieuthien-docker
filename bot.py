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
    print("DEBUG: Import các module thành công.", file=sys.stderr)
except ImportError as e:
    print(f"LỖI KHỞI ĐỘNG: Không thể import module: {e}", file=sys.stderr)
    sys.exit(1)

# === Khởi tạo ứng dụng FastAPI và Telegram Application ===
app = FastAPI(docs_url=None, redoc_url=None)

telegram_app: Application = ApplicationBuilder().token(TOKEN).build()

@app.on_event("startup")
async def startup_event():
    """
    Hàm này chạy một lần duy nhất khi ứng dụng ASGI khởi động.
    """
    print("DEBUG: Bắt đầu quá trình khởi động ứng dụng (startup_event)...", file=sys.stderr)
    try:
        # Đăng ký các handlers cho bot
        register_handlers(telegram_app)
        print("DEBUG: Đăng ký các handlers thành công.", file=sys.stderr)

        # Khởi tạo Application
        await telegram_app.initialize()
        print("DEBUG: Telegram Application đã được initialize.", file=sys.stderr)

        # Thiết lập Webhook
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
        json_data = await request.json()
        print(f"DEBUG: Dữ liệu JSON từ webhook: {json_data}", file=sys.stderr)
        
        update = Update.de_json(json_data, telegram_app.bot)
        
        await telegram_app.process_update(update)
        print(f"DEBUG: Đã xử lý thành công update_id: {update.update_id}", file=sys.stderr)

        return Response(status_code=200)

    except Exception as e:
        print(f"LỖI trong telegram_webhook: {e}", file=sys.stderr)
        return Response(status_code=500)

# === Chạy cục bộ để test (sử dụng uvicorn) ===
if __name__ == '__main__':
    print("DEBUG: Chạy cục bộ bằng uvicorn...", file=sys.stderr)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
