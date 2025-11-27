# Dockerfile
FROM python:3.11-slim

# Install tesseract for OCR (if you want the fallback)
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# expose port
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
