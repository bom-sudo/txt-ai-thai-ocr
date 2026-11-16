---
title: Pwa Thai Ocr
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# PWACareVision - OpenThai 2.0 OCR API

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
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

สามารถนำขึ้น Render ได้ 2 รูปแบบตามความต้องการใช้งาน:

### แบบที่ 1: Private Service (`pserv`) — แนะนำสำหรับ Internal Backend
> เหมาะสำหรับใช้เป็น Microservice ภายในระบบ Render เพื่อให้ Backend ตัวอื่น (เช่น Node.js, Python, Golang) เรียกใช้เท่านั้น โดยไม่เปิดให้คนนอกเข้าถึงทางอินเทอร์เน็ตโดยตรง

1. Push โค้ดนี้ขึ้น **GitHub Repository** ของคุณ (Public หรือ Private ก็ได้)
2. ไปที่หน้าสร้าง Private Service: [Render Project New Private Service](https://dashboard.render.com/project/prj-dbt8mhei0phs73f127e0/pserv/new)
3. เลือกหรือวาง URL ของ GitHub Repository ของคุณ
4. ตั้งค่าดังนี้:
   - **Name:** `pwa-thai-ocr` (หรือชื่อที่คุณต้องการ)
   - **Region:** `Singapore` (แนะนำสำหรับประเทศไทย)
   - **Branch:** `main`
   - **Runtime:** `Docker` (Render จะตรวจพบ `Dockerfile` อัตโนมัติ)
   - **Plan:** `Starter` ($7/mo - Private Service บน Render เริ่มต้นที่ Starter)
   - **Health Check Path:** `/health`
5. กด **Create Private Service**
6. **วิธีเรียกใช้งานจาก Service อื่นใน Render:**
   - Private Network Hostname: `http://pwa-thai-ocr:10000`
   - Endpoint: `http://pwa-thai-ocr:10000/ocr`

---

### แบบที่ 2: Web Service (`web`) — รองรับ Free Plan / เข้าถึงจากอินเทอร์เน็ตได้
> เหมาะสำหรับต้องการ Public URL เพื่อให้ Frontend (PWA, Mobile App, Web) ยิงมาที่ API ได้โดยตรง

1. ใน Render Dashboard คลิก **New +** > **Web Service**
2. เลือก GitHub Repository ของคุณ
3. ตั้งค่า:
   - **Runtime:** `Docker`
   - **Plan:** `Free` หรือ `Starter`
   - **Health Check Path:** `/health`
4. เมื่อสร้างเสร็จ คุณจะได้ URL สาธารณะ เช่น: `https://pwa-thai-ocr.onrender.com`

---

## 💻 การรัน Local / Docker

### วิธีที่ 1: รันด้วย Docker Compose (แนะนำ)
```bash
# สั่ง build และ start container
docker compose up -d --build

# ดู log
docker compose logs -f
```
บริการจะเปิดที่ `http://localhost:10000`

### วิธีที่ 2: รันด้วย Docker CLI ทั่วไป
```bash
docker build -t pwa-thai-ocr .
docker run -p 10000:10000 -e PORT=10000 pwa-thai-ocr
```

### วิธีที่ 3: รันตรงด้วย Python (ไม่ต้องใช้ Docker)
```bash
# 1. ติดตั้ง dependencies
pip install -r requirements.txt

# 2. รันแอป (ระบบจะดาวน์โหลดโมเดล OpenThai 2.0 อัตโนมัติในครั้งแรก)
python app.py
# หรือ
uvicorn app:app --host 0.0.0.0 --port 10000
```

---

## 📡 API Reference & ตัวอย่างการใช้งาน

Interactive Swagger UI ดูได้ที่: `http://localhost:10000/docs` หรือ `<URL>/docs`

### 1. ตรวจสอบสถานะระบบ (`GET /health`)
```bash
curl http://localhost:10000/health
```
**Response:**
```json
{
  "status": "ok",
  "ready": true,
  "engine": "OpenThai 2.0"
}
```

---

### 2. OCR ด้วยการอัปโหลดไฟล์ภาพ (`POST /ocr`)
ส่งไฟล์ภาพแบบ `multipart/form-data` (รองรับ `.jpg`, `.jpeg`, `.png`, `.pdf`)

```bash
curl -X POST "http://localhost:10000/ocr" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.jpg"
```

---

### 3. OCR ด้วย Base64 (`POST /ocr/base64`)
ส่งภาพที่แปลงเป็น Base64 หรือ Data URL ใน JSON

```bash
curl -X POST "http://localhost:10000/ocr/base64" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "filename": "slip.jpg"
  }'
```

---

### 4. รูปแบบ Response ตัวอย่าง
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

ใน repo มีไฟล์ `test_client.py` สำหรับทดสอบส่งภาพไปที่ API:

```bash
# ทดสอบกับ Localhost
python test_client.py http://localhost:10000 receipt.jpg

# ทดสอบกับ Render Web Service
python test_client.py https://pwa-thai-ocr.onrender.com receipt.jpg
```

---

## ⚙️ Environment Variables ที่ปรับแต่งได้

| ตัวแปร | ค่าเริ่มต้น | รายละเอียด |
|---|---|---|
| `PORT` | `10000` | พอร์ตที่ Uvicorn จะเปิดรับ (Render กำหนดให้อัตโนมัติ) |
| `OCR_THREADS` | `2` | จำนวน Thread ของ CPU สำหรับประมวลผล OCR (ปรับได้ตามขนาดของ Instance) |
| `MODEL_DIR` | `/app/OpenThai2.0-OCR-Text` | โฟลเดอร์เก็บ Model weights |

---

## 📄 License
- Model: [iapp/OpenThai2.0-OCR-Text](https://huggingface.co/iapp/OpenThai2.0-OCR-Text) (Apache-2.0 License)
- Code: MIT License
