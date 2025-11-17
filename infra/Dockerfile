# =========================================================
# Aegis Agent Fleet - Dockerfile
# =========================================================
# Base Python image
FROM python:3.10-slim

# Work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY ../requirements.txt /app/requirements.txt

# Install Python requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy project into container
COPY .. /app

# Expose FastAPI port
EXPOSE 8080

# Command to run API service
CMD ["uvicorn", "services.orchestrator.api:app", "--host", "0.0.0.0", "--port", "8080"]
