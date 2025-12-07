# 使用 Python 3.10 軽量版
FROM python:3.10-slim

# 工作目錄
WORKDIR /app

# 複製 Python 需求
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY backend/requirements.txt ./requirements.txt

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 開放容器 8000 port
EXPOSE 8000

# 使用 Uvicorn 啟動 FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
