FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_APP=app.py \
    SESSION_TYPE=filesystem \
    SESSION_FILE_DIR=/app/flask_session

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with proper permissions for sessions
RUN mkdir -p /app/flask_session && \
    chmod 777 /app/flask_session

# Create non-root user for security
RUN useradd -m appuser
USER appuser

# Expose port
EXPOSE $PORT

# Run with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60 "app:app"