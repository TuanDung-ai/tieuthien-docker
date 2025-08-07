# bot.py

import threading
from fastapi import FastAPI
import uvicorn
from telegram.ext import Application
from config import (
    BOT_TOKEN,
    PORT,
    POLLING_TIMEOUT,
    READ_TIMEOUT,
    WRITE_TIMEOUT,
)
from handlers.register_handlers import register_handlers
from core.logging_config import setup_logging
import telegram

print("PTB version:", telegram.__version__)  # In version đang chạy

# Thiết lập logging
setup_logging()

# FastAPI app
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

# Chạy FastAPI server
def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=PORT)

# Khởi động Telegram bot
def main():
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing.")

    # PTB v21.2+ supports get_updates_timeout
    app_bot = (
        Application.builder()
        .token(BOT_TOKEN)
        .get_updates_timeout(POLLING_TIMEOUT)
        .get_updates_read_timeout(READ_TIMEOUT)
        .get_updates_write_timeout(WRITE_TIMEOUT)
        .build()
    )

    register_handlers(app_bot)

    print(f"✅ Bot is running with polling timeout={POLLING_TIMEOUT}s...")
    app_bot.run_polling()

# Chạy song song FastAPI + Telegram bot
if __name__ == "__main__":
    threading.Thread(target=run_uvicorn, daemon=True).start()
    main()
