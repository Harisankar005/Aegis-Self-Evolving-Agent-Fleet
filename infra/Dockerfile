# ============================
# Aegis - Multi-Agent System
# Production Dockerfile
# ============================

FROM python:3.10-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install OS dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY services/ ./services/
COPY evaluation/ ./evaluation/
COPY docs/ ./docs/

# Expose FastAPI/Orchestrator port
EXPOSE 8080

# Startup command (FastAPI server)
CMD ["uvicorn", "services.orchestrator.orchestrator:app", "--host", "0.0.0.0", "--port", "8080"]
