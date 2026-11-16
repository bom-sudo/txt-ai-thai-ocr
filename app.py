import sys
import os
import io
import base64
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image

# Path to OpenThai2.0 model weights and code
MODEL_DIR = Path(os.environ.get("MODEL_DIR", "/app/OpenThai2.0-OCR-Text"))
if not MODEL_DIR.exists():
    MODEL_DIR = Path("OpenThai2.0-OCR-Text")

# Auto-download model weights if not present (useful for local Python dev or non-Docker env)
if not MODEL_DIR.exists() or not (MODEL_DIR / "det.onnx").exists():
    try:
        from huggingface_hub import snapshot_download
        print(f"Model not found at {MODEL_DIR}. Downloading iapp/OpenThai2.0-OCR-Text from Hugging Face...")
        snapshot_download(repo_id="iapp/OpenThai2.0-OCR-Text", local_dir=str(MODEL_DIR))
        print("Model downloaded successfully.")
    except Exception as e:
        print(f"Warning: Failed to auto-download model: {e}")

sys.path.insert(0, str(MODEL_DIR))

# Initialize LineOCR Engine
ocr_engine = None
try:
    from runtime.line_engine import LineOCR
    threads = int(os.environ.get("OCR_THREADS", "2"))
    ocr_engine = LineOCR(str(MODEL_DIR), threads=threads)
    print(f"OpenThai 2.0 LineOCR Engine initialized successfully (threads={threads}).")
except Exception as e:
    print(f"Warning: LineOCR Engine not initialized: {e}")

app = FastAPI(
    title="PWACareVision OpenThai 2.0 OCR API",
    description="Thai & English OCR service for receipts and documents powered by iapp/OpenThai2.0-OCR-Text",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Base64OCRRequest(BaseModel):
    image: str  # Data URL or pure base64 string
    filename: Optional[str] = "receipt.jpg"

def run_ocr_on_file(file_path: str):
    if not ocr_engine:
        raise HTTPException(status_code=500, detail="OCR engine is not loaded on this server.")
    
    results = ocr_engine(file_path)
    lines = []
    full_text_list = []

    for item in results:
        text = str(item.get("text", "")).strip()
        conf = float(item.get("confidence", 1.0))
        box = item.get("box") or item.get("bbox") or []
        if text:
            lines.append({
                "text": text,
                "confidence": round(conf, 4),
                "box": box
            })
            full_text_list.append(text)

    full_text = "\n".join(full_text_list)
    return {
        "success": True,
        "line_count": len(lines),
        "text": full_text,
        "lines": lines
    }

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "PWACareVision OpenThai 2.0 OCR API",
        "model": "iapp/OpenThai2.0-OCR-Text",
        "ready": ocr_engine is not None,
        "endpoints": {
            "health": "GET /health",
            "docs": "GET /docs",
            "upload": "POST /ocr (multipart/form-data)",
            "base64": "POST /ocr/base64 (application/json)"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "ok" if ocr_engine is not None else "degraded",
        "ready": ocr_engine is not None,
        "engine": "OpenThai 2.0"
    }

@app.post("/ocr")
async def ocr_upload(file: UploadFile = File(...)):
    suffix = Path(file.filename or "receipt.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        data = run_ocr_on_file(tmp_path)
        data["filename"] = file.filename
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Processing Error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/ocr/base64")
async def ocr_base64(req: Base64OCRRequest):
    img_str = req.image
    if "," in img_str:
        img_str = img_str.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(img_str)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 payload: {str(e)}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        data = run_ocr_on_file(tmp_path)
        data["filename"] = req.filename
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Processing Error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "10000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
