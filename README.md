---
title: TXT AI Thai OCR
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# txt-ai-thai-ocr - OpenThai 2.0 OCR API

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/bom-sudo/txt-ai-thai-ocr)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![OpenThai 2.0](https://img.shields.io/badge/Model-iapp%2FOpenThai2.0--OCR--Text-orange.svg)](https://huggingface.co/iapp/OpenThai2.0-OCR-Text)

บริการ OCR ภาษาไทยและภาษาอังกฤษความเร็วสูง ทำงานบน CPU 100% (ไม่ต้องใช้ GPU) พัฒนาด้วย **FastAPI** และขับเคลื่อนด้วยโมเดล **OpenThai 2.0** (`iapp/OpenThai2.0-OCR-Text` จาก iApp Technology) 

ออกแบบมาให้พร้อม Deploy ได้ทันทีทั้งบน **Render** (Private Service / Web Service), **Hugging Face Spaces**, **Docker** และ **Localhost**

---

## 🚀 จุดเด่น (Features)

- **ความเร็วสูง & ประหยัดทรัพยากร:** โมเดลขนาดเล็กเพียง ~4.2 MB ใช้ RAM เพียง ~450 MB รันบน CPU ทั่วไปได้สบาย (ประมวลผล ~0.3 - 0.5 วินาทีต่อหน้า)
- **แม่นยำสูง:** รองรับทั้งภาษาไทยและอังกฤษ พร้อมระบบ Auto-deskew (หมุน/จัดองศาภาพอัตโนมัติ) และอ่านตัวหนังสือสีขาวบนพื้นดำได้
- **รองรับ Render 100%:** รองรับ `$PORT` อัตโนมัติ (Render, Hugging Face, Local), มี `/health` endpoint สำหรับ health check
- **Dual Endpoint:** รองรับทั้งแบบอัปโหลดไฟล์ตรง (`multipart/form-data`) และส่งภาพ Base64 (`application/json`)
- **ข้อมูลครบถ้วน:** ส่งกลับทั้งข้อความรวม (`text`), รายการบรรทัด (`lines`), ค่าความมั่นใจ (`confidence`), และพิกัดกรอบข้อความ (`box`)

---

## 🛠️ การนำขึ้น Render (Deployment Guide)

### วิธีที่ 1: Deploy ผ่าน Render Dashboard (Private Service)
เข้าไปที่ลิงก์ของโปรเจกต์คุณ:
👉 **[Render Project New Private Service](https://dashboard.render.com/project/prj-dbt8mhei0phs73f127e0/pserv/new)**

1. ใส่ Git Repository URL:
   ```text
   https://github.com/bom-sudo/txt-ai-thai-ocr
   ```
2. ตั้งค่าบริการ:
   - **Name:** `txt-ai-thai-ocr` (หรือชื่อที่คุณต้องการ)
   - **Region:** `Singapore` (แนะนำสำหรับประเทศไทย)
   - **Branch:** `main`
   - **Runtime:** `Docker` (Render ตรวจพบ `Dockerfile` อัตโนมัติ)
   - **Plan:** `Starter` ($7/mo)
   - **Health Check Path:** `/health`
3. กด **Create Private Service**
4. **Internal Network URL สำหรับ Service อื่นใน Render:**
   - Base URL: `http://txt-ai-thai-ocr:10000`
   - OCR Endpoint: `http://txt-ai-thai-ocr:10000/ocr`

---

### วิธีที่ 2: Deploy เป็น Web Service (Public API & รองรับ Free Tier)
หากต้องการ Public URL ให้ Frontend ยิงมาได้ตรงๆ หรือต้องการใช้ Free Plan ของ Render:
1. กดที่ปุ่ม: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/bom-sudo/txt-ai-thai-ocr)
2. หรือใน Render Dashboard เลือก **New +** > **Web Service** > วาง `https://github.com/bom-sudo/txt-ai-thai-ocr`
3. เลือก Plan เป็น **Free** หรือ **Starter**
4. จะได้รับ Public URL เช่น `https://txt-ai-thai-ocr.onrender.com`

---

## 💻 การรัน Local / Docker

### รันด้วย Docker Compose
```bash
docker compose up -d --build
```
บริการจะเปิดที่ `http://localhost:10000`

### รันตรงด้วย Python
```bash
pip install -r requirements.txt
python app.py
```

---

## 📡 API Reference & ตัวอย่างการใช้งาน

Interactive Swagger UI ดูได้ที่: `http://localhost:10000/docs` หรือ `<YOUR_RENDER_URL>/docs`

### 1. ตรวจสอบสถานะระบบ (`GET /health`)
```bash
curl http://localhost:10000/health
```
```json
{
  "status": "ok",
  "ready": true,
  "engine": "OpenThai 2.0"
}
```

### 2. OCR ด้วยการอัปโหลดไฟล์ภาพ (`POST /ocr`)
```bash
curl -X POST "http://localhost:10000/ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.jpg"
```

### 3. OCR ด้วย Base64 (`POST /ocr/base64`)
```bash
curl -X POST "http://localhost:10000/ocr/base64" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "filename": "slip.jpg"
  }'
```

### 4. ตัวอย่าง Response
```json
{
  "success": true,
  "line_count": 3,
  "filename": "receipt.jpg",
  "text": "ใบเสร็จรับเงิน / ใบกำกับภาษี\nโรงพยาบาลกรุงเทพ\nยอดชำระทั้งสิ้น 1,500.00 บาท",
  "lines": [
    {
      "text": "ใบเสร็จรับเงิน / ใบกำกับภาษี",
      "confidence": 0.9852,
      "box": [[32, 10], [280, 10], [280, 42], [32, 42]]
    },
    {
      "text": "โรงพยาบาลกรุงเทพ",
      "confidence": 0.9921,
      "box": [[30, 50], [210, 50], [210, 80], [30, 80]]
    },
    {
      "text": "ยอดชำระทั้งสิ้น 1,500.00 บาท",
      "confidence": 0.9784,
      "box": [[35, 120], [310, 120], [310, 155], [35, 155]]
    }
  ]
}
```

---

## 🧪 สคริปต์ทดสอบ (Test Client)

```bash
# ทดสอบกับ Localhost
python test_client.py http://localhost:10000 receipt.jpg

# ทดสอบกับ Render Web Service
python test_client.py https://txt-ai-thai-ocr.onrender.com receipt.jpg
```

---

## ⚙️ Environment Variables

| ตัวแปร | ค่าเริ่มต้น | รายละเอียด |
|---|---|---|
| `PORT` | `10000` | พอร์ตที่ Uvicorn จะเปิดรับ (Render กำหนดให้อัตโนมัติ) |
| `OCR_THREADS` | `2` | จำนวน Thread ของ CPU สำหรับประมวลผล OCR |
| `MODEL_DIR` | `/app/OpenThai2.0-OCR-Text` | โฟลเดอร์เก็บ Model weights |

---

## 📄 License
- Model: [iapp/OpenThai2.0-OCR-Text](https://huggingface.co/iapp/OpenThai2.0-OCR-Text) (Apache-2.0 License)
- Code: MIT License
