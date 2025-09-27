# Base stage with common dependencies
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Listener service staging
FROM base AS listener
COPY listener/ ./
CMD ["python", "listener_app_sqs.py"]

# DNS worker service staging
FROM base AS dns-worker
COPY dns-worker/ ./
CMD ["python", "dns_worker_app.py"]