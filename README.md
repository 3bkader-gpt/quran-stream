# 🎙️ QuranStream

> **Live Audio Streaming Platform** - Stream Quranic radio stations to Telegram and other RTMP platforms with zero-downtime channel switching.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange.svg)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 About

QuranStream is a professional live audio streaming platform designed to stream Quranic radio stations to RTMP platforms like Telegram, Facebook Live, YouTube Live, and more. The platform features zero-downtime channel switching, allowing you to seamlessly switch between 126 pre-configured radio stations without interrupting your live stream.

### Topics

`python` `fastapi` `ffmpeg` `streaming` `rtmp` `live-streaming` `audio-streaming` `quran` `radio` `telegram` `docker` `web-application` `rest-api` `audio-processing` `multimedia` `real-time` `streaming-platform` `islamic-content` `live-audio` `web-interface`

## ✨ Features

- 🎵 **Zero-Downtime Streaming** - Seamless continuous audio streaming
- 🔄 **Live Channel Switching** - Switch between stations without interrupting the stream
- 📻 **126 Quranic Radio Stations** - Pre-configured stations from mp3quran.com
- 🌐 **Modern Web Interface** - User-friendly dashboard for stream management
- ⚡ **High Performance** - Advanced process management with threading
- 🐳 **Docker Support** - Ready for deployment on Render, Heroku, and other platforms
- 🔒 **Production Ready** - Built with FastAPI for scalability

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- FFmpeg installed on your system
- RTMP server URL and stream key (e.g., Telegram Live Stream)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/quran-stream.git
cd quran-stream

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open your browser at `http://localhost:8000`

## 📖 Usage

1. **Access the Web Interface**
   - Navigate to `http://localhost:8000` in your browser

2. **Configure RTMP Settings**
   - Enter your RTMP Server URL (e.g., `rtmp://live-api-s.facebook.com:80/rtmp/`)
   - Enter your Stream Key

3. **Start Streaming**
   - Select a radio station from the dropdown menu
   - Click the **Play** button to start streaming

4. **Switch Channels**
   - Select a different station from the dropdown
   - The stream will automatically switch without interruption

## 🏗️ Project Structure

```
stream/
├── main.py                 # Main application (FastAPI + Stream Manager)
├── mp3quran_radios.m3u     # Radio stations playlist (126 stations)
├── templates/
│   └── index.html          # Web interface
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration for deployment
├── .dockerignore          # Docker ignore file
├── Procfile               # Process file for Heroku
└── render.yaml            # Render deployment configuration
```

## 🛠️ Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **FFmpeg** - Powerful multimedia framework for audio streaming and transcoding
- **Uvicorn** - Lightning-fast ASGI server
- **Jinja2** - Template engine for web interface
- **Python Threading** - Advanced process management and synchronization
- **Raw PCM Piping** - Zero-downtime channel switching technique

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t quran-stream .

# Run the container
docker run -p 8000:8000 quran-stream
```

### Deploy to Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Docker support"
   git push
   ```

2. **Configure on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click **New +** → **Web Service**
   - Connect your GitHub repository
   - Configure settings:
     - **Name:** `quran-stream` (or your preferred name)
     - **Runtime:** Select **Docker** (important!)
     - **Region:** Choose the closest region
     - **Instance Type:** Free (for testing) or Starter (for production)
   - Click **Create Web Service**

3. **Keep-Alive for Free Tier**
   - Free tier services sleep after 15 minutes of inactivity
   - Use [UptimeRobot](https://uptimerobot.com/) to ping your service every 5 minutes
   - This prevents the service from sleeping and keeps your stream running

## 📡 API Endpoints

- `GET /` - Web interface
- `GET /api/stations` - Get list of available radio stations
- `POST /api/start` - Start streaming (requires: `url`, `rtmp_server`, `key`)
- `POST /api/stop` - Stop current stream
- `GET /api/status` - Get current stream status

## 🔧 How It Works

The application uses a sophisticated two-process architecture:

1. **Feed Process** - Downloads and decodes audio from the source radio station
2. **Main Process** - Encodes and streams to RTMP server

Both processes communicate via raw PCM pipes, allowing seamless channel switching without interrupting the RTMP connection.

## 📝 Configuration

### Environment Variables

- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

### Adding Custom Stations

Edit `mp3quran_radios.m3u` and add your station URLs (one per line).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Radio stations provided by [mp3quran.com](https://mp3quran.net/)
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [FFmpeg](https://ffmpeg.org/)

---

**Made with ❤️ for the Muslim community**
