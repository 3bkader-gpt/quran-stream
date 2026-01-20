<div align="center">

# 📻 Quran Stream

### Live Quran Radio Streaming to Telegram via RTMP

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg)](https://fastapi.tiangolo.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Audio%20Pipeline-007808.svg)](https://ffmpeg.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

**Local Web Controller • RTMP Output • Multiple Quran Radio Stations**

[Features](#-features) • [Architecture](#-architecture) • [Docker Deployment](#-docker-deployment) • [Local Run](#-local-run)

</div>

---

## 🎯 Overview

Quran Stream is a **local controller** for streaming Quran radio to Telegram (or any RTMP destination).

It:

- Reads a list of radio streams from `mp3quran_radios.m3u`
- Lets you select a station from a web UI
- Streams the selected station via FFmpeg pipeline to your RTMP server/key
- Provides a simple FastAPI-based control panel

---

## 🌟 Features

- 📡 **Live audio streaming** from Quran radio sources
- 🔗 **RTMP output** compatible with Telegram and other RTMP consumers
- 🌐 **Web UI** to manage station selection and stream status
- 🧰 **FFmpeg-based pipeline** for robust audio handling
- 🐳 **Docker support** for easy deployment (single service)

---

## 🏗 Architecture

- `main.py` – FastAPI app + embedded HTTP streaming server + FFmpeg management
- `templates/` – Jinja2 templates for the control panel
- `mp3quran_radios.m3u` – list of radio stream URLs
- `Dockerfile` – container image including FFmpeg and app
- `docker-compose.yml` – one-service Compose file for easier deployment

---

## 🐳 Docker Deployment

### Prerequisites

- Docker
- Docker Compose plugin (`docker compose`)

### Quick Start

```bash
git clone https://github.com/3bkader-gpt/quran-stream.git
cd quran-stream

# Build image and run container
docker compose up -d --build
```

This will:

- Build image from `Dockerfile`
- Start container on port **8000** (mapped to host `8000`)

Now open in browser:

```text
http://<server-ip>:8000/
```

### Managing the container

```bash
# View status
docker compose ps

# Show logs
docker compose logs -f

# Stop & remove container
docker compose down
```

---

## 💻 Local Run (without Docker)

### Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the app

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

Make sure **FFmpeg** is installed on the host (the Docker image already includes FFmpeg).

---

## 📄 License

This project is open-source under the MIT License.
