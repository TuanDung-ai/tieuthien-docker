# Sử dụng Python 3.10-slim làm image cơ sở để giảm kích thước
FROM python:3.10-slim

# Thiết lập biến môi trường
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Cài đặt các phụ thuộc hệ thống cần thiết cho python-telegram-bot
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép các tệp cần thiết cho việc cài đặt
COPY requirements.txt .
COPY deploy_setup.py .

# Cài đặt các gói Python vào môi trường ảo
RUN python -m venv $VIRTUAL_ENV && \
    $VIRTUAL_ENV/bin/pip install --upgrade pip && \
    $VIRTUAL_ENV/bin/pip install -r requirements.txt

# Sao chép toàn bộ mã nguồn của ứng dụng
COPY . /app

# Lệnh chạy ứng dụng khi container khởi động
# Chạy script set_webhook_once trước, sau đó mới khởi động gunicorn
CMD [ "sh", "-c", "python deploy_setup.py && gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT} bot:app" ]
