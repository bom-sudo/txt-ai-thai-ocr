import sys
import os
import io
import base64
import shutil
import secrets
import tempfile
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
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

# Initialize Thai word segmenter (OpenThai2.0-LATTE-WordSeg-Lite, ทำงาน offline บน CPU)
segmenters = {}
try:
    from openthai_latte_wordseg_lite import Segmenter
    for _unit in ("long", "short", "minimal"):
        segmenters[_unit] = Segmenter(unit=_unit)
    print("LATTE-WordSeg-Lite initialized successfully.")
except Exception as e:
    print(f"Warning: WordSeg not initialized: {e}")

def segment_text(text: str, unit: str = "short") -> List[str]:
    # ตัดคำไทยทีละบรรทัด เพื่อให้ผลลัพธ์ไม่ข้ามบรรทัดของ OCR
    seg = segmenters.get(unit)
    if not seg:
        raise HTTPException(status_code=503, detail="Word segmentation is not available on this server.")
    words: List[str] = []
    for line in text.splitlines():
        if line.strip():
            words.extend(w for w in seg.tokenize(line) if w.strip())
    return words

def apply_segmentation(data: dict, unit: Optional[str]) -> dict:
    if not unit:
        return data
    if unit not in ("long", "short", "minimal"):
        raise HTTPException(status_code=400, detail="segment must be one of: long, short, minimal")
    data["segment_unit"] = unit
    data["words"] = segment_text(data["text"], unit)
    for line in data["lines"]:
        line["words"] = segment_text(line["text"], unit)
    return data

# Security & API Key Authentication
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False, description="API Key via x-api-key header")
bearer_scheme = HTTPBearer(auto_error=False, description="API Key via Authorization: Bearer <key>")

def verify_api_key(
    header_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
):
    expected_key = os.environ.get("API_KEY", "sk-thai-ocr-2026").strip()
    provided_key = header_key or (bearer.credentials if bearer else None)

    if not provided_key or not secrets.compare_digest(provided_key, expected_key):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing API Key. Provide via 'x-api-key' header or 'Authorization: Bearer <key>'."
        )
    return provided_key

app = FastAPI(
    title="PWACareVision OpenThai 2.0 OCR API",
    description="Secure Thai & English OCR service powered by iapp/OpenThai2.0-OCR-Text. Protected by API Key authentication.",
    version="2.1.0"
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
    segment: Optional[str] = None  # long | short | minimal -> เพิ่มผลตัดคำ

class SegmentRequest(BaseModel):
    text: str
    unit: str = "short"  # long | short | minimal

def run_ocr_on_file(file_path: str):
    if not ocr_engine:
        raise HTTPException(status_code=500, detail="OCR engine is not loaded on this server.")
    
    if hasattr(ocr_engine, "read"):
        res = ocr_engine.read(file_path)
    elif callable(ocr_engine):
        res = ocr_engine(file_path)
    else:
        raise HTTPException(status_code=500, detail="LineOCR has no read method.")

    if isinstance(res, dict):
        full_text = res.get("text", "")
        raw_lines = res.get("lines", [])
    elif isinstance(res, list):
        full_text = "\n".join([str(item.get("text", "")).strip() for item in res if item.get("text")])
        raw_lines = res
    else:
        full_text = str(res)
        raw_lines = []

    lines = []
    for item in raw_lines:
        text = str(item.get("text", "")).strip()
        conf = float(item.get("confidence", 1.0))
        box = item.get("box") or item.get("bbox") or []
        if text:
            lines.append({
                "text": text,
                "confidence": round(conf, 4),
                "box": box
            })

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
        "wordseg_ready": bool(segmenters),
        "auth_required": True,
        "auth_methods": [
            "Header: x-api-key: <YOUR_API_KEY>",
            "Header: Authorization: Bearer <YOUR_API_KEY>"
        ],
        "endpoints": {
            "health": "GET /health (public)",
            "docs": "GET /docs (Swagger UI with Authorize button)",
            "upload": "POST /ocr (multipart/form-data, requires API key)",
            "base64": "POST /ocr/base64 (application/json, requires API key)",
            "segment": "POST /segment (Thai word segmentation, requires API key). OCR endpoints accept segment=long|short|minimal"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "ok" if ocr_engine is not None else "degraded",
        "ready": ocr_engine is not None,
        "engine": "OpenThai 2.0"
    }

@app.post("/ocr", dependencies=[Depends(verify_api_key)])
async def ocr_upload(file: UploadFile = File(...), segment: Optional[str] = None):
    suffix = Path(file.filename or "receipt.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        data = run_ocr_on_file(tmp_path)
        data["filename"] = file.filename
        return apply_segmentation(data, segment)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Processing Error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/ocr/base64", dependencies=[Depends(verify_api_key)])
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
        return apply_segmentation(data, req.segment)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Processing Error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/segment", dependencies=[Depends(verify_api_key)])
def segment(req: SegmentRequest):
    if req.unit not in ("long", "short", "minimal"):
        raise HTTPException(status_code=400, detail="unit must be one of: long, short, minimal")
    words = segment_text(req.text, req.unit)
    return {"success": True, "unit": req.unit, "word_count": len(words), "words": words}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "10000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
