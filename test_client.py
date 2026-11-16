"""
Sample Python client to test the OpenThai 2.0 OCR API.
Usage:
    python test_client.py [URL] [IMAGE_PATH]

Example:
    python test_client.py http://localhost:10000 receipt.jpg
    python test_client.py https://pwa-thai-ocr.onrender.com receipt.jpg
"""

import sys
import base64
import requests
from pathlib import Path

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:10000"
IMAGE_PATH = sys.argv[2] if len(sys.argv) > 2 else None

print(f"=== Testing OCR API at: {BASE_URL} ===")

# 1. Health Check
try:
    health_resp = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"[*] GET /health -> [{health_resp.status_code}] {health_resp.json()}")
except Exception as e:
    print(f"[!] Error contacting /health: {e}")

if not IMAGE_PATH:
    print("\nTip: Pass an image path to test OCR recognition:")
    print("     python test_client.py http://localhost:10000 path/to/slip.jpg")
    sys.exit(0)

image_file = Path(IMAGE_PATH)
if not image_file.exists():
    print(f"[!] File not found: {IMAGE_PATH}")
    sys.exit(1)

# 2. Test Multipart Form Upload (/ocr)
print(f"\n[*] Testing POST /ocr with {image_file.name}...")
with open(image_file, "rb") as f:
    files = {"file": (image_file.name, f, "image/jpeg")}
    resp = requests.post(f"{BASE_URL}/ocr", files=files, timeout=60)

if resp.status_code == 200:
    data = resp.json()
    print(f"[+] OCR Success! Lines recognized: {data.get('line_count')}")
    print("--- Extracted Text ---")
    print(data.get("text"))
    print("----------------------")
else:
    print(f"[!] OCR Failed [{resp.status_code}]: {resp.text}")

# 3. Test Base64 Endpoint (/ocr/base64)
print(f"\n[*] Testing POST /ocr/base64 with {image_file.name}...")
with open(image_file, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "image": f"data:image/jpeg;base64,{b64}",
    "filename": image_file.name
}
resp_b64 = requests.post(f"{BASE_URL}/ocr/base64", json=payload, timeout=60)
if resp_b64.status_code == 200:
    print(f"[+] Base64 OCR Success! Lines: {resp_b64.json().get('line_count')}")
else:
    print(f"[!] Base64 OCR Failed [{resp_b64.status_code}]: {resp_b64.text}")
