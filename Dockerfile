FROM python:3.10-slim

# Prevent Python from writing bytecode and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000 \
    OCR_THREADS=2

# Install system libraries needed by OpenCV, ONNX Runtime, and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download iapp/OpenThai2.0-OCR-Text model weights into container image during build
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='iapp/OpenThai2.0-OCR-Text', local_dir='/app/OpenThai2.0-OCR-Text')"

# Copy application code
COPY app.py .

# Expose ports (10000 for Render, 7860 for Hugging Face Spaces, 8000 default)
EXPOSE 10000 7860 8000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Start Uvicorn dynamically binding to $PORT provided by Render, HF Spaces, or default 10000
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}"]
