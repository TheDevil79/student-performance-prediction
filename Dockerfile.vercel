# ==============================================================================
# Dockerfile for Student Performance Prediction Web Service
# Compatible with local Docker, Render, AWS EC2, and container runtimes.
# ==============================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    MODEL_PATH=model.joblib \
    STATIC_DIR=static

# Set working directory
WORKDIR /app

# Install system dependencies (curl for healthchecks if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Upgrade pip, then install ONLY runtime deps (grep out test-only lines)
# This avoids pulling pytest/httpx into the production image.
RUN pip install --no-cache-dir --upgrade pip && \
    grep -v '^#\|^pytest\|^httpx\|^$' requirements.txt | pip install --no-cache-dir -r /dev/stdin

# Copy application source code, trained model, evaluation report, and static frontend
# Note: data/ (raw CSV) is NOT needed at runtime - model.joblib is the deployed artefact.
COPY app/ ./app/
COPY static/ ./static/
COPY train.py .
COPY model.joblib .
COPY evaluation_report.json .

# Create non-root user for security best practices
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose default port
EXPOSE 8000

# Health check instruction for Docker / container runtimes
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start Uvicorn on 0.0.0.0 and dynamically bind to $PORT env var (for Render/AWS/local)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
