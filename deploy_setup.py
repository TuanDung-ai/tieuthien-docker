# deploy_setup.py
import os
import asyncio
import sys
from telegram.ext import ApplicationBuilder

# Lấy TOKEN và URL từ biến môi trường
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ZEABUR_PUBLIC_URL = os.getenv("ZEABUR_URL")
PORT = int(os.getenv("PORT", 8080))

if not TOKEN:
    print("LỖI: TELEGRAM_BOT_TOKEN không được thiết lập trong deploy_setup.py!", file=sys.stderr)
    sys.exit(1)
if not ZEABUR_PUBLIC_URL:
    print("LỖI: ZEABUR_URL không được thiết lập trong deploy_setup.py! Không thể đặt webhook.", file=sys.stderr)
    sys.exit(1)

WEBHOOK_PATH = "/telegram-webhook"
WEBHOOK_URL = f"{ZEABUR_PUBLIC_URL}{WEBHOOK_PATH}"

async def set_webhook_once():
    """Thiết lập webhook cho bot Telegram."""
    print(f"DEBUG (deploy_setup): Bắt đầu thiết lập webhook tại URL: {WEBHOOK_URL}", file=sys.stderr)
    try:
        app = ApplicationBuilder().token(TOKEN).build()
        await app.bot.set_webhook(url=WEBHOOK_URL)
        print("DEBUG (deploy_setup): Đặt webhook thành công.", file=sys.stderr)
    except Exception as e:
        print(f"LỖI (deploy_setup): Không thể đặt webhook: {e}", file=sys.stderr)
        sys.exit(1) # Thoát với lỗi nếu không thể đặt webhook

if __name__ == "__main__":
    asyncio.run(set_webhook_once())
