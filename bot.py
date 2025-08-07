import logging
import threading
from fastapi import FastAPI
from telegram.ext import Application
import uvicorn
from config import TELEGRAM_BOT_TOKEN, PORT
from handlers.register_handlers import register_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

app = FastAPI()

@app.get("/")
@app.head("/")
async def healthcheck():
    return {"status": "ok", "message": "Bot is alive."}

def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=PORT)

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing.")
    
    app_bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    register_handlers(app_bot)
    print("✅ Bot is running...")
    app_bot.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_uvicorn, daemon=True).start()
    main()
