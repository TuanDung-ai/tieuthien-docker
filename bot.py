# bot.py
import threading
from fastapi import FastAPI
import uvicorn
from telegram.ext import Application
from config import BOT_TOKEN, PORT, POLLING_TIMEOUT
from handlers.register_handlers import register_handlers
from core.logging_config import setup_logging

setup_logging()

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

def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=PORT)

def main():
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing.")

    app_bot = Application.builder().token(BOT_TOKEN).build()
    register_handlers(app_bot)
    print(f"\u2705 Bot is running with polling timeout={POLLING_TIMEOUT}s...")
    app_bot.run_polling(timeout=POLLING_TIMEOUT)

if __name__ == "__main__":
    threading.Thread(target=run_uvicorn, daemon=True).start()
    main()
