FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libportaudio2 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config.template.json .

ENV TRANSCRIPTION_CONFIG=/app/config.json
ENV PYTHONUNBUFFERED=1

VOLUME ["/app/recordings", "/app/config.json"]

CMD ["python", "-m", "src.main"]
