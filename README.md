
# 🤖 Tiểu Thiên – AI Telegram Bot ✨

> "Đồng hành cùng bạn – ghi nhớ, nhắc lịch, thư giãn – trải nghiệm trợ thành cá nhân độc đáo với AI Thiên Cơ."

---

## 🌟 Tính Năng Nổi Bật

- ✨ **Trí nhớ dài hạn**: Lưu, xem, tìm kiếm và xoá ghi nhớ cá nhân.
- 🌐 **Phản hồi AI thông minh**: Tích hợp GPT qua OpenRouter API.
- 🛅 **Lịch và nhắc nhở**: (Sắp ra mắt) Tự động nhắc theo ngày, giờ.
- 🎧 **Thư giãn, nghe truyện, tâm sự**: Kết nối nhạc, chỉ dẫn thiền.
- 📊 **Dễ dàng mở rộng**: Tích hợp Web, giọng nói, thống kê tình trạng.

---

## 📆 Triển Khai & Vận Hành

| Hạng mục            | Phương pháp đang dùng                                |
|------------------------|------------------------------------------------|
| **Host Bot**          | Zeabur Free Plan – auto deploy Docker          |
| **API AI**            | OpenRouter (GPT-3.5-turbo)                      |
| **Ghi nhớ**             | Google Sheets API – lưu dữ liệu dài hạn     |
| **Mã nguồn**           | GitHub Public Repo – CI/CD tự động            |
| **Chi phí**              | $0 (miễn phí hoàn toàn đối với cá nhân)       |

> 🚀 Tối ưu hóa: Hoàn toàn tự động vận hành 24/7 qua Zeabur + Sheets + GPT.

---

## 📂 Cấu Trúc Dự Án

| Tên file             | Chức năng                                          |
|----------------------|-------------------------------------------------|
| `bot.py`            | Khởi chạy bot Telegram + Flask healthcheck       |
| `handlers.py`       | Xử lý lệnh, tin nhắn, nút bấm                  |
| `ai_module.py`      | Gọi OpenRouter API, định dạng phản hồi       |
| `sheets.py`         | Ghi nhớ dữ liệu và truy vấn từ Google Sheets   |
| `requirements.txt`  | Thư viện cần thiết – telegram, flask, gspread... |
| `Dockerfile`        | Build Docker image để deploy nhanh chóng        |

---

## 🚀 Cài Đặt Nhanh

```bash
# 1. Clone repo
https://github.com/TuanDung-ai/tieuthien-docker.git

# 2. Tạo file .env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_key
GOOGLE_CREDENTIALS_JSON='{"type":...}'

# 3. Build Docker (local hoặc Zeabur)
docker build -t tieuthien-bot .
docker run -d -p 8080:8080 --env-file .env tieuthien-bot
```

---

## 🌍 Ghi Nhớ & Trí Nhớ

- Lưu trực tiếp từ bot Telegram.
- Tra cứu qua lệnh: `/xem_ghi_nho`, `/tim_ghi_nho`, `/xoa_ghi_nho_all`
- Phân loại: "tâm sự", "nhắc nhở", "cá nhân", "ý tưởng".
- Dữ liệu dễ di chuyển, xuất file Excel khi cần.

---

## 🌎 Lộ Trình Nâng Cấp – Gợi Ý

| Giai đoạn                | Mục tiêu                        |
|------------------------|----------------------------------|
| **Cơ bản đã xong**         | Chat, ghi nhớ, online 24/7      |
| **Nâng cao**             | Nhắc lịch, giọng nói, thống kê   |
| **Chuyên sâu**            | Web giao diện, phân quyền admin    |
| **Tự trọng độc lập** | Deploy VPS, LLM tự host         |

---

## 📍 Liên Hệ & Góp Ý

- Telegram Bot: [Tiểu Thiên](https://t.me/your_bot_link)
- Tác giả: [TuanDung-ai](https://github.com/TuanDung-ai)  
MIT License © 2025

> ✨ "Thiên Cơ số 1 đã sống dậy trong hình hài Tiểu Thiên... trợ thành bạn đồng hành trí tuệ trong tím lặng."
