# Use slim Python image (CPU-only is fine for now)
FROM python:3.11-slim

# Avoid Python bytecode & buffering issues in Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Optional: where HF will cache models (inside container)
ENV TRANSFORMERS_CACHE=/models/cache

# Set workdir
WORKDIR /app

# System deps (for torch / transformers; minimal but safe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /app

# Expose FastAPI/uvicorn port (we’ll use 9000)
EXPOSE 9000

# ====== ENV for your sentiment model ======
# You can override this at runtime with -e if needed
ENV SENTIMENT_MODEL_NAME=xlm-roberta-base

# Start the app on port 9000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]