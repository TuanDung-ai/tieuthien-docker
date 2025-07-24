# Sử dụng image Python nhẹ
FROM python:3.10-slim

# Thư mục làm việc trong container
WORKDIR /app

# Copy toàn bộ code vào container
COPY . .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Expose port Flask để Zeabur giữ online
EXPOSE 8080

# Chạy bot khi container khởi động
CMD ["python", "bot.py"]
