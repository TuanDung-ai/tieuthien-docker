# Tiểu Thiên – AI Telegram Bot

🤖 **Tiểu Thiên** là một trợ lý AI cá nhân hóa, hoạt động trên nền tảng Telegram. Bot sử dụng OpenRouter (GPT) để phản hồi thông minh, có thể ghi nhớ dài hạn, trò chuyện, nhắc lịch và thư giãn cùng người dùng.

> "Bạn cần gì tiếp theo? – Ghi nhớ, Lịch, Hay thư giãn?"

---

## 🌟 Tính năng chính

* **Trí nhớ dài hạn**: Lưu – xem – xóa ghi nhớ cá nhân.
* **Phản hồi AI tự nhiên**: Kết nối GPT (qua OpenRouter).
* **Giao diện trực quan**: Nút bấm, menu đơn giản, dễ dùng.
* **Có thể mở rộng**: Lịch, nhắc việc, phát nhạc…

---

## 📦 Cấu trúc dự án

| Tệp tin            | Mô tả chức năng                                                   |
| ------------------ | ----------------------------------------------------------------- |
| `bot.py`           | Tập tin khởi chạy chính, kết nối Telegram và xử lý logic bot.     |
| `ai_module.py`     | Xử lý API GPT từ OpenRouter, định dạng phản hồi AI.               |
| `memory_module.py` | Quản lý ghi nhớ JSON, hỗ trợ phân loại và tìm kiếm.               |
| `web.py`           | Web server đơn giản giúp uptime bot trên các nền tảng như Zeabur. |
| `Dockerfile`       | Tạo container Docker cho bot, hỗ trợ deploy Zeabur.               |
| `requirements.txt` | Danh sách thư viện Python cần thiết: telegram, flask, requests... |
| `bot_goc.py`       | Bản sao gốc dự phòng bot.py để phục hồi nếu cần.                  |

---

## 🚀 Cài đặt & Khởi chạy

### 1. Clone repo

```bash
git clone https://github.com/TuanDung-ai/tieuthien-docker.git
cd tieuthien-docker
```

### 2. Tạo file `.env`

```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_key
```

### 3. Build và chạy Docker

```bash
docker build -t tieuthien-bot .
docker run -d -p 8080:8080 --env-file .env tieuthien-bot
```

### Hoặc deploy với Zeabur (Auto Docker)

* Import repo → Zeabur → Add Service → chọn Docker.
* Khai báo biến môi trường → Build → Deploy.

---

## 📂 Dữ liệu & Ghi nhớ

* Tất cả ghi nhớ người dùng lưu tại `memory.json`
* **Cấu trúc nâng cấp**:

  * Phân loại theo: `note`, `calendar`, `reminder`, ...
  * Có thể tìm kiếm, lọc, tra cứu tự động khi bot phản hồi.
  * Hỗ trợ xóa theo ngày hoặc theo loại.

Ví dụ:

```json
{
  "123456789": [
    {"type": "note", "content": "Mua sữa", "time": "2025-07-25T10:00"},
    {"type": "reminder", "content": "Cuộc họp 3h chiều", "time": "2025-07-25T09:00"}
  ]
}
```

---

## 🛠️ Mở rộng sắp tới

* Tích hợp lịch – nhắc việc tự động theo giờ.
* Giao diện Web quản lý ghi nhớ.
* Kết nối API nhạc thư giãn, truyện kể.

---

## 📜 License

MIT License © 2025 [TuanDung-ai](https://github.com/TuanDung-ai)

---

## 📬 Liên hệ & Góp ý

* Telegram Bot: [Tiểu Thiên](https://t.me/your_bot_link)
* Tác giả: [TuanDung-ai](https://github.com/TuanDung-ai) – Always building AI

---
