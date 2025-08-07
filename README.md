# 🤖 Bot Thiên Cơ - Trợ Lý AI Ghi Nhớ

Một Telegram Bot đơn giản nhưng mạnh mẽ: **có trí nhớ cloud, phản hồi thông minh, giọng điệu tự nhiên**.

## 🚀 Tính năng chính

| Tính năng        | Mô tả                                                         |
| ---------------- | ------------------------------------------------------------- |
| 🤖 Trí tuệ AI    | Giao tiếp với GPT-3.5-turbo qua OpenRouter                    |
| 🧠 Ghi nhớ Cloud | Lưu, truy xuất, xóa ghi nhớ theo từng người dùng qua Supabase |
| 📚 Lệnh cơ bản   | /ghi\_nho, /xem\_nho, /xoa\_nho, /xoa\_tatca, /tro\_giup      |
| 🛡️ Tách module  | Dễ nâng cấp, bảo trì, triển khai Zeabur hoặc Replit cực nhanh |

## 🧩 Cấu trúc thư mục

```bash
📁 root/
├── bot.py                   # Điểm khởi động bot + FastAPI
├── config.py                # Cấu hình môi trường (TOKEN, KEY, MODEL,...)
├── requirements.txt         # Thư viện cần thiết
├── .env.example             # Mẫu file môi trường
│
├── core/
│   ├── logging_config.py    # Logging chuẩn
│   └── state_manager.py     # Quản lý trạng thái user
│
├── modules/
│   ├── ai_module.py         # Xử lý phản hồi AI
│   ├── memory_manager.py    # Thao tác ghi nhớ
│   └── buttons.py           # Giao diện nút
│
├── memory/
│   └── db_supabase.py       # Kết nối Supabase
│
├── handlers/
│   ├── commands.py          # Các lệnh Telegram
│   ├── message_handler.py   # Xử lý tin nhắn AI
│   └── register_handlers.py # Đăng ký bot
```

## ⚙️ Cài đặt & Chạy bot

### 1. Clone repo & cài môi trường

```bash
git clone https://github.com/ban-ten-bot/thien-co.git
cd thien-co
cp .env.example .env
```

### 2. Thiết lập biến môi trường `.env`

```ini
TELEGRAM_BOT_TOKEN=your_bot_token
OPENROUTER_API_KEY=your_openrouter_key
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_anon_key
PORT=8080
```

### 3. Cài thư viện & chạy bot

```bash
pip install -r requirements.txt
python bot.py
```

> ✨ Truy cập bot trên Telegram để thử ngay!

## 🧪 Lệnh thử

```bash
/ghi_nho Hôm nay trời đẹp quá
/xem_nho
/xoa_nho 1
/xoa_tatca
```

## ✅ Triển khai gợi ý

* [ ] Zeabur: chọn template Python, dán token vào Environment
* [ ] Replit: bật UptimeRobot ping endpoint `/status`

## 📜 Giấy phép

MIT License - Bạn được phép sử dụng & chỉnh sửa thoải mái

---

> Bot Thiên Cơ - AI giản dị nhưng mạnh mẽ.
