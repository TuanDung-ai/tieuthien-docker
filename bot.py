# bot.py
import os
import logging
from telegram.ext import Application
from modules.handlers import register_handlers

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    """Khởi động bot."""
    # Lấy token từ biến môi trường
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

    # Tạo Application và truyền token vào
    application = Application.builder().token(token).build()

    # Đăng ký tất cả các handlers từ file handlers.py
    register_handlers(application)

    # Chạy bot ở chế độ polling
    print("✅ Bot đang chạy ở chế độ polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
