FROM python:3.12-slim

# Install SDL2 dependencies for PyGame
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libasound2-dev \
    libx11-6 \
    libxext6 \
    libxcursor1 \
    libxrandr2 \
    libxss1 \
    libxi6 \
    libxinerama1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Avoid Python pyc files & buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "game/main.py"]
