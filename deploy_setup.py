import os
import asyncio
import sys
import httpx

# Lấy TOKEN và URL từ biến môi trường
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ZEABUR_PUBLIC_URL = os.getenv("ZEABUR_URL")

if not TOKEN:
    print("LỖI: TELEGRAM_BOT_TOKEN không được thiết lập!", file=sys.stderr)
    sys.exit(1)
if not ZEABUR_PUBLIC_URL:
    print("LỖI: ZEABUR_URL không được thiết lập! Không thể đặt webhook.", file=sys.stderr)
    sys.exit(1)

WEBHOOK_PATH = "/telegram-webhook"
WEBHOOK_URL = f"{ZEABUR_PUBLIC_URL}{WEBHOOK_PATH}"

async def set_webhook_once():
    """Thiết lập webhook cho bot Telegram một lần duy nhất."""
    print(f"DEBUG (deploy_setup): Bắt đầu thiết lập webhook tại URL: {WEBHOOK_URL}", file=sys.stderr)
    
    # Sử dụng httpx để gửi yêu cầu bất đồng bộ
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}&drop_pending_updates=True")
            if response.status_code == 200 and response.json().get("ok"):
                print("DEBUG (deploy_setup): Đặt webhook thành công.", file=sys.stderr)
                return True
            else:
                print(f"LỖI (deploy_setup): Không thể đặt webhook. Phản hồi từ Telegram: {response.text}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"LỖI (deploy_setup): Không thể đặt webhook: {e}", file=sys.stderr)
            return False

if __name__ == '__main__':
    # Chạy hàm set_webhook_once một lần duy nhất
    success = asyncio.run(set_webhook_once())
    if not success:
        sys.exit(1) # Thoát với lỗi nếu không thể đặt webhook
