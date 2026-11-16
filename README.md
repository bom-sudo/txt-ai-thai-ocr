---
title: TXT AI Thai OCR
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# txt-ai-thai-ocr - OpenThai 2.0 OCR API (Protected with API Key)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/bom-sudo/txt-ai-thai-ocr)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![OpenThai 2.0](https://img.shields.io/badge/Model-iapp%2FOpenThai2.0--OCR--Text-orange.svg)](https://huggingface.co/iapp/OpenThai2.0-OCR-Text)

บริการ OCR ภาษาไทยและภาษาอังกฤษความเร็วสูง ทำงานบน CPU 100% (ไม่ต้องใช้ GPU) พัฒนาด้วย **FastAPI** และขับเคลื่อนด้วยโมเดล **OpenThai 2.0** (`iapp/OpenThai2.0-OCR-Text` จาก iApp Technology) 

🔒 **ระบบป้องกันความปลอดภัย:** มีระบบล็อกด้วย **API Key Authentication** ป้องกันบุคคลภายนอกแอบยิงใช้งาน

---

## 🔑 ข้อมูล API Key & การตั้งค่า

### 1. วิธีแนบ API Key ในการเรียกใช้งาน
สามารถส่ง API Key มาได้ 2 รูปแบบ:
- **ผ่าน Header `x-api-key`:**
  ```http
  x-api-key: sk-thai-ocr-2026
  ```
- **หรือผ่าน Header `Authorization` (Bearer Token):**
  ```http
  Authorization: Bearer sk-thai-ocr-2026
  ```

### 2. วิธีเปลี่ยน API Key บน Render
1. ไปที่ Render Dashboard ➔ เลือก service `txt-ai-thai-ocr`
2. ไปที่แถบ **Environment**
3. ค้นหาหรือกด **Add Environment Variable**:
   - **Key:** `API_KEY`
   - **Value:** `รหัสลับใหม่ที่คุณต้องการ` (เช่น `my-secret-key-999`)
4. กด **Save Changes** (ระบบจะรีสตาร์ทและใช้ Key ใหม่ทันที)

*(หากไม่ได้ตั้งค่าไว้ใน Environment ระบบจะใช้ค่าเริ่มต้นคือ `sk-thai-ocr-2026`)*

---

## 🚀 จุดเด่น (Features)

- **ความปลอดภัยสูง:** ล็อก API ด้วย `API_KEY` รองรับทั้ง Header `x-api-key` และ `Bearer Token`
- **ความเร็วสูง & ประหยัดทรัพยากร:** โมเดลขนาดเล็กเพียง ~4.2 MB ใช้ RAM เพียง ~450 MB รันบน CPU ทั่วไปได้สบาย (ประมวลผล ~0.3 - 0.5 วินาทีต่อหน้า)
- **แม่นยำสูง:** รองรับทั้งภาษาไทยและอังกฤษ พร้อมระบบ Auto-deskew (หมุน/จัดองศาภาพอัตโนมัติ)
- **รองรับ Render 100%:** รองรับ `$PORT` อัตโนมัติ, มี `/health` endpoint สาธารณะสำหรับ Render Health Check
- **Dual Endpoint:** รองรับทั้งแบบอัปโหลดไฟล์ตรง (`POST /ocr`) และส่งภาพ Base64 (`POST /ocr/base64`)

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
   - **Name:** `txt-ai-thai-ocr`
   - **Region:** `Singapore`
   - **Branch:** `main`
   - **Runtime:** `Docker`
   - **Plan:** `Starter` ($7/mo)
   - **Health Check Path:** `/health`
3. เพิ่ม Environment Variable:
   - `API_KEY`: `sk-thai-ocr-2026` (หรือรหัสที่คุณต้องการ)
4. กด **Create Private Service**

---

### วิธีที่ 2: Deploy เป็น Web Service (Public API & รองรับ Free Tier)
1. ใน Render Dashboard เลือก **New +** > **Web Service** > วาง `https://github.com/bom-sudo/txt-ai-thai-ocr`
2. เลือก Plan เป็น **Free** หรือ **Starter**
3. เพิ่ม Environment Variable `API_KEY`
4. เมื่อ Deploy สำเร็จจะได้ URL เช่น: `https://txt-ai-thai-ocr.onrender.com`

---

## 📡 API Reference & ตัวอย่างการใช้งาน

Interactive Swagger UI ดูได้ที่: `https://txt-ai-thai-ocr.onrender.com/docs`
*(สามารถกดปุ่ม **Authorize 🔓** ที่มุมขวาบนของหน้าเว็บ Swagger แล้วกรอก API Key เพื่อทดสอบได้ทันที)*

### 1. ตรวจสอบสถานะระบบ (`GET /health`) — *Public ไม่ต้องใส่ Key*
```bash
curl https://txt-ai-thai-ocr.onrender.com/health
```
```json
{
  "status": "ok",
  "ready": true,
  "engine": "OpenThai 2.0"
}
```

---

### 2. OCR ด้วยการอัปโหลดไฟล์ภาพ (`POST /ocr`) — *ต้องใส่ Key*
```bash
curl -X POST "https://txt-ai-thai-ocr.onrender.com/ocr" \
  -H "x-api-key: sk-thai-ocr-2026" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.jpg"
```

---

### 3. OCR ด้วย Base64 (`POST /ocr/base64`) — *ต้องใส่ Key*
```bash
curl -X POST "https://txt-ai-thai-ocr.onrender.com/ocr/base64" \
  -H "x-api-key: sk-thai-ocr-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "filename": "slip.jpg"
  }'
```

---

### 4. ตัวอย่างการเรียกใช้งานใน JavaScript (Fetch API)
```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch("https://txt-ai-thai-ocr.onrender.com/ocr", {
  method: "POST",
  headers: {
    "x-api-key": "sk-thai-ocr-2026"  // หรือใส่ API Key ที่คุณตั้งไว้
  },
  body: formData
});

if (response.status === 401) {
  console.error("API Key ไม่ถูกต้อง!");
} else {
  const data = await response.json();
  console.log("ข้อความที่ตรวจพบ:", data.text);
}
```

---

## 🧪 สคริปต์ทดสอบ (Test Client)

```bash
# ทดสอบกับ Render Web Service
python test_client.py https://txt-ai-thai-ocr.onrender.com receipt.jpg sk-thai-ocr-2026
```

---

## ⚙️ Environment Variables

| ตัวแปร | ค่าเริ่มต้น | รายละเอียด |
|---|---|---|
| `API_KEY` | `sk-thai-ocr-2026` | รหัส API Key สำหรับปลดล็อกใช้งาน endpoint `/ocr` |
| `PORT` | `10000` | พอร์ตที่ Uvicorn จะเปิดรับ (Render กำหนดให้อัตโนมัติ) |
| `OCR_THREADS` | `2` | จำนวน Thread ของ CPU สำหรับประมวลผล OCR |
| `MODEL_DIR` | `/app/OpenThai2.0-OCR-Text` | โฟลเดอร์เก็บ Model weights |

---

## 📄 License
- Model: [iapp/OpenThai2.0-OCR-Text](https://huggingface.co/iapp/OpenThai2.0-OCR-Text) (Apache-2.0 License)
- Code: MIT License
