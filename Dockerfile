# 使用 Python 3.10 輕量版
FROM python:3.10-slim

# 工作目錄
WORKDIR /app

# 複製 Python 需求檔案
COPY requirements.txt ./requirements.txt

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製後端程式碼
COPY backend/ ./backend/

# 複製前端資料（靜態檔案）
COPY frontend/ ./frontend/

# 開放容器 8000 port
EXPOSE 8000

# 使用 Uvicorn 啟動 FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]