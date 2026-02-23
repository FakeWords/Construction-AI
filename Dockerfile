FROM python:3.11-slim

# Cache bust v2
RUN echo "v2"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

The key additions are `libpq-dev` and `gcc` — psycopg2 needs those system libraries to install. Then:
```
git add Dockerfile
git commit -m "Fix Dockerfile for psycopg2"
git push origin main
