# bot.py
import os
import logging
import threading
from telegram.ext import Application
from handlers.register_handlers import register_handlers
from fastapi import FastAPI
import uvicorn

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# --- Khởi tạo và chạy FastAPI Web Server (dùng cho UptimeRobot) ---
app = FastAPI()

# Thêm decorator @app.head để xử lý yêu cầu HEAD từ UptimeRobot
@app.get("/")
@app.head("/")
async def home():
    """Một endpoint đơn giản để UptimeRobot ping."""
    return {"status": "ok", "message": "Bot is alive."}

# Hàm chạy uvicorn trong một luồng riêng
def run_uvicorn():
    """Chạy web server FastAPI."""
    try:
        # Lấy cổng từ biến môi trường và đảm bảo nó là số nguyên
        port = int(os.environ.get("PORT", 8080))
        uvicorn.run(app, host="0.0.0.0", port=port)
    except ValueError as e:
        print(f"Lỗi: PORT không phải là số. Chi tiết: {e}")
        # Log lỗi và thoát nếu không thể chuyển đổi PORT thành số nguyên
        exit(1)

# --- Khởi tạo và chạy Telegram Bot Polling ---
def main():
    """Khởi động bot polling."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

    application = Application.builder().token(token).build()
    register_handlers(application)
    
    print("✅ Bot đang chạy ở chế độ polling...")
    application.run_polling()

if __name__ == "__main__":
    # Tạo và khởi động luồng cho web server
    web_server_thread = threading.Thread(target=run_uvicorn, daemon=True)
    web_server_thread.start()
    
    # Chạy bot polling trong luồng chính
    main()
