FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-rus \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /invextract

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY  . .

EXPOSE 8000

CMD ["python","-m", "src.api.main"]
