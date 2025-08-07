# bot.py
import threading
from fastapi import FastAPI
import uvicorn
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN, PORT
from handlers.register_handlers import register_handlers
from core.logging_config import setup_logging

# Thiết lập logging chuẩn
setup_logging()

# Khởi tạo FastAPI app
app = FastAPI()

@app.get("/")
@app.head("/")
async def healthcheck():
    return {"status": "ok", "message": "Bot is alive."}

@app.get("/status")
async def status():
    return {
        "status": "running",
        "bot": "Thien Co",
        "version": "2.0",
        "author": "You",
        "message": "Bot is healthy and ready"
    }

# Chạy FastAPI song song
def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=PORT)

# Hàm khởi động bot
def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing.")

    app_bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    register_handlers(app_bot)
    print("✅ Bot is running...")
    app_bot.run_polling()

# Chạy FastAPI và bot song song
if __name__ == "__main__":
    threading.Thread(target=run_uvicorn, daemon=True).start()
    main()
