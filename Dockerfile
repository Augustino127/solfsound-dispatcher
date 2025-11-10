# SolfSound Dispatcher - Production Docker Image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install SolfSound
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/output /app/uploads /app/logs

# Expose ports
EXPOSE 8000

# Environment variables
ENV SOLFSOUND_HOST=0.0.0.0
ENV SOLFSOUND_PORT=8000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/')"

# Run web server by default
CMD ["python", "run_web.py"]
