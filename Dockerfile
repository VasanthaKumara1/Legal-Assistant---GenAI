
# Use Python 3.11 slim image

# Legal Assistant GenAI Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app


# Install system dependencies for OCR and document processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app_user

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs data

# Set environment variables
ENV PYTHONPATH=/app
ENV UPLOAD_DIRECTORY=uploads
ENV LOG_FILE=logs/app.log

RUN mkdir -p /app/data/uploads /app/data/processed /app/logs

# Set ownership to app_user
RUN chown -R app_user:app_user /app

# Switch to non-root user
USER app_user

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
