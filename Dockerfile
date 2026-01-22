FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    rubberband-cli \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY Audios/ ./Audios/

RUN mkdir -p /app/uploads

EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/watermark_testing/api/app.py"]