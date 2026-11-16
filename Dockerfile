FROM python:3.10-slim

# Install system libraries needed by OpenCV and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download iapp/OpenThai2.0-OCR-Text model files into container image during build
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='iapp/OpenThai2.0-OCR-Text', local_dir='/app/OpenThai2.0-OCR-Text')"

# Copy application code
COPY app.py .

# Hugging Face Spaces port
EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
