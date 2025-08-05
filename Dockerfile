# Sử dụng image Python nhẹ
FROM python:3.10-slim

# Cài đặt git để pip có thể cài supabase-py từ GitHub
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc trong container
WORKDIR /app

# Copy toàn bộ mã nguồn từ máy vào container
COPY . /app

# Cài đặt thư viện cần thiết từ requirements.txt (đã có gunicorn)
RUN pip install --no-cache-dir -r requirements.txt

# Khai báo cổng Flask hoặc bot giữ cho container không chết
EXPOSE 8080

# Chạy script thiết lập webhook một lần, sau đó khởi động Gunicorn
CMD ["sh", "-c", "python deploy_setup.py && gunicorn -w 4 -b 0.0.0.0:${PORT} bot:web_app"]
