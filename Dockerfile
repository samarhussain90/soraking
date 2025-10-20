# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directories
RUN mkdir -p output/logs output/analysis output/videos output/uploads

# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Run with gunicorn for production (eventlet for WebSocket support)
# Single worker to avoid coordination issues, but with extended timeout
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--worker-class", "eventlet", "--workers", "1", "--timeout", "600", "--worker-connections", "1000", "server:app"]
