# Dockerfile

# Sử dụng image Python nhẹ và hiện đại
FROM python:3.10-slim

# Cài đặt git để pip có thể cài các gói từ repo (nếu cần)
# Giữ lại để phòng trường hợp dependency của supabase-py cần
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements trước để tận dụng cache của Docker
# Chỉ khi file này thay đổi, lớp layer này mới chạy lại
COPY requirements.txt /app/

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn còn lại của ứng dụng
COPY . /app

# Khai báo cổng mà ứng dụng sẽ lắng nghe
EXPOSE 8080

# === THAY ĐỔI: Cập nhật lệnh CMD cho FastAPI và Gunicorn ===
# - Không cần chạy `deploy_setup.py` nữa vì logic đã ở trong sự kiện startup.
# - Sử dụng worker `-k uvicorn.workers.UvicornWorker` để chạy ứng dụng ASGI.
# - Trỏ đến ứng dụng FastAPI `bot:app` (file bot.py, đối tượng app).
# - Bạn có thể điều chỉnh số lượng worker (-w) tùy theo gói dịch vụ của bạn (2-4 là phổ biến).
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:${PORT}", "bot:app"]
