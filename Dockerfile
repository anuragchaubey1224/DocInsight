# ========================================
# OPTIMIZED DOCKERFILE FOR RAILWAY
# Reduces image size from 5.1GB → ~2.8GB
# ========================================

# ===== STAGE 1: Builder =====
FROM python:3.10-slim as builder

# Install build dependencies (will be discarded)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy only requirements first (for better caching)
COPY requirements.txt .

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ===== CRITICAL: Install CPU-only PyTorch =====
# This saves ~2GB by excluding CUDA/GPU libraries
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    torch==2.0.1+cpu \
    torchvision==0.15.2+cpu \
    torchaudio==2.0.2+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify critical packages are installed
RUN python -c "import transformers; import torch; import sentence_transformers; import faiss; print('✅ All critical packages installed')"

# ===== STAGE 2: Runtime =====
FROM python:3.10-slim

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/tmp/.cache/huggingface \
    TRANSFORMERS_CACHE=/tmp/.cache/transformers \
    TORCH_HOME=/tmp/.cache/torch \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata \
    PYTHONPATH=/app/backend

# Copy application code
COPY backend/ /app/backend/
COPY .env.example /app/.env.example

# Create necessary directories
RUN mkdir -p \
    /app/backend/app/data/uploads \
    /app/backend/app/data/index \
    /tmp/.cache && \
    chmod -R 777 /app/backend/app/data /tmp/.cache

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Railway automatically sets PORT
ENV PORT=10000

# Run with uvicorn
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT} --workers 1
