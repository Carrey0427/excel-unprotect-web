# backend/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from .excel_unprotect import remove_protection

app = FastAPI(
    title="Excel Unprotect API",
    description="Remove sheet/workbook protection from Excel files",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許任何來源 (包含 file:/// )
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/unprotect")
async def unprotect_excel(file: UploadFile = File(...)):
    allowed_ext = [".xlsx", ".xlsm", ".xls"]
    filename = file.filename.lower()

    if not any(filename.endswith(ext) for ext in allowed_ext):
        raise HTTPException(status_code=400, detail="Only Excel files are supported (.xlsx, .xlsm, .xls)")

    # 讀取上傳內容
    file_bytes = await file.read()

    # 呼叫我們的 Excel 解保護函式
    new_file_bytes, new_filename = remove_protection(file_bytes, file.filename)

    # 使用 StreamingResponse 回傳檔案供下載
    return StreamingResponse(
        iter([new_file_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename={new_filename}',
            "x-filename": new_filename  # 🔥 自訂 Header 防止被忽略
        }
    )


@app.get("/")
def home():
    return {"status": "Excel Unprotect API running", "message": "Go to /docs to test the API."}
