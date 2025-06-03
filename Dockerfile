FROM python:3.9

RUN apt-get update && apt-get install -y \
    libssl-dev \
    zlib1g-dev \
    libc++1 \
    libc++-dev \
    libstdc++6 \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser
USER appuser

WORKDIR /home/appuser/app

COPY --chown=appuser . .

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p sessions/tdlib sessions/telethon

CMD ["python", "main.py"]
