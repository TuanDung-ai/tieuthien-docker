# Dockerfile

# Sử dụng image Python nhẹ và hiện đại
FROM python:3.10-slim

# Cài đặt git để pip có thể cài các gói từ repo (nếu cần)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements trước để tận dụng cache của Docker
COPY requirements.txt /app/

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn còn lại của ứng dụng
COPY . /app

# Khai báo cổng mà ứng dụng sẽ lắng nghe
EXPOSE 8080

# === SỬA LỖI: Chuyển CMD sang dạng shell để thay thế biến ${PORT} ===
# Bằng cách bọc lệnh gunicorn trong `["sh", "-c", "..."]`, chúng ta yêu cầu
# Docker khởi chạy một shell. Shell này sẽ thay thế `${PORT}` bằng giá trị
# thực (ví dụ: 8080) trước khi thực thi lệnh gunicorn.
CMD ["sh", "-c", "gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT} bot:app"]
