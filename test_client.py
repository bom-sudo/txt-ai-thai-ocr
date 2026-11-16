"""
Sample Python client to test the OpenThai 2.0 OCR API.
Usage:
    python test_client.py [URL] [IMAGE_PATH] [API_KEY]

Example:
    python test_client.py https://txt-ai-thai-ocr.onrender.com receipt.jpg sk-thai-ocr-2026
"""

import sys
import os
import base64
import requests
from pathlib import Path

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:10000"
IMAGE_PATH = sys.argv[2] if len(sys.argv) > 2 else None
API_KEY = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("API_KEY", "sk-thai-ocr-2026")

print(f"=== Testing OCR API at: {BASE_URL} ===")
print(f"[*] Using API Key: {API_KEY[:4]}***{API_KEY[-4:] if len(API_KEY) > 8 else ''}")

# 1. Health Check (Public endpoint)
try:
    health_resp = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"[*] GET /health -> [{health_resp.status_code}] {health_resp.json()}")
except Exception as e:
    print(f"[!] Error contacting /health: {e}")

if not IMAGE_PATH:
    print("\nTip: Pass an image path to test OCR recognition:")
    print("     python test_client.py https://txt-ai-thai-ocr.onrender.com receipt.jpg sk-thai-ocr-2026")
    sys.exit(0)

image_file = Path(IMAGE_PATH)
if not image_file.exists():
    print(f"[!] File not found: {IMAGE_PATH}")
    sys.exit(1)

headers = {
    "x-api-key": API_KEY
}

# 2. Test Multipart Form Upload (/ocr)
print(f"\n[*] Testing POST /ocr with {image_file.name}...")
with open(image_file, "rb") as f:
    files = {"file": (image_file.name, f, "image/jpeg")}
    resp = requests.post(f"{BASE_URL}/ocr", headers=headers, files=files, timeout=60)

if resp.status_code == 200:
    data = resp.json()
    print(f"[+] OCR Success! Lines recognized: {data.get('line_count')}")
    print("--- Extracted Text ---")
    print(data.get("text"))
    print("----------------------")
elif resp.status_code == 401:
    print(f"[!] Unauthorized [401]: API Key is missing or invalid! Details: {resp.text}")
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
resp_b64 = requests.post(f"{BASE_URL}/ocr/base64", headers=headers, json=payload, timeout=60)
if resp_b64.status_code == 200:
    print(f"[+] Base64 OCR Success! Lines: {resp_b64.json().get('line_count')}")
elif resp_b64.status_code == 401:
    print(f"[!] Unauthorized [401]: API Key is missing or invalid!")
else:
    print(f"[!] Base64 OCR Failed [{resp_b64.status_code}]: {resp_b64.text}")
