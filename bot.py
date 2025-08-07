# bot.py
import threading
import logging
from fastapi import FastAPI
import uvicorn

from telegram.ext import Application
from handlers.register_handlers import register_handlers
from config import TELEGRAM_BOT_TOKEN, PORT

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# FastAPI app
app = FastAPI()

@app.get("/")
@app.head("/")
async def home():
    return {"status": "ok", "message": "Bot is alive."}

def run_uvicorn():
    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    except Exception as e:
        print(f"❌ Lỗi khởi chạy FastAPI: {e}")
        exit(1)

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    register_handlers(application)

    print("✅ Bot đang chạy ở chế độ polling...")
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_uvicorn, daemon=True).start()
    main()
