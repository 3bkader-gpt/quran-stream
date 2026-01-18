<div align="center">

# 📻 Quran Stream

### Live Audio Streaming to Telegram via RTMP

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)](https://fastapi.tiangolo.com/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-orange.svg)](https://ffmpeg.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**Live Audio Streaming • Telegram Integration • Advanced Audio Processing**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](#-contributing)

[العربية](README-ar.md) | [English](#-quran-stream)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Technologies Used](#-technologies-used)
- [Contributing](#-contributing)

---

## 🎯 Overview

**Quran Stream** is a live audio streaming system to Telegram via RTMP. It allows you to stream Quranic radio directly to your Telegram channels easily and simply.

### ✨ Why Quran Stream?

- 📡 **High-Quality Live Streaming** - Clear and stable audio streaming
- 🔗 **Seamless Telegram Integration** - Easy streaming to your channels
- 🎵 **Advanced Audio Processing** - Using FFmpeg for audio processing and conversion
- 🌐 **Simple Web Interface** - Full control from your browser

---

## 🌟 Features

### 🚀 Main Features

| Feature | Description |
|---------|-------------|
| 📡 **Live Streaming** | Live audio streaming of Quranic radio |
| 🔗 **Telegram Integration** | Live streaming to Telegram channels via RTMP |
| 🎵 **Audio Processing** | Using FFmpeg for audio processing and conversion |
| 🌐 **Web Interface** | Simple web interface for stream control |
| 🐳 **Docker Support** | Easy deployment using Docker |
| ⚡ **High Performance** | FastAPI for ultra-fast speed |

### 📻 Supported Stations

- mp3quran.net stations
- Other Islamic radio stations
- Custom station support

---

## 📦 Requirements

Before starting, make sure you have installed:

- **Python** 3.8 or higher
- **FFmpeg** (required for audio processing)
- **Telegram** account
- **Docker** (optional for deployment)

### Installing FFmpeg

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download FFmpeg from https://ffmpeg.org/download.html
```

---

## 🚀 Installation

### Method 1: Standard Installation

```bash
# 1. Clone the repository
git clone https://github.com/3bkader-gpt/quran-stream.git
cd quran-stream

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Run the application
python main.py
```

### Method 2: Using Docker

```bash
# Clone the repository
git clone https://github.com/3bkader-gpt/quran-stream.git
cd quran-stream

# Build the image
docker build -t quran-stream .

# Run the container
docker run -p 8000:8000 quran-stream
```

---

## ⚙️ Configuration

### Telegram RTMP Setup

1. Create a Telegram channel
2. Get RTMP URL from Telegram
3. Add the URL in settings

### Customizing Stations

Edit `mp3quran_radios.m3u` to add or modify radio stations:

```m3u
#EXTM3U
#EXTINF:-1,Quranic Radio
http://stream.example.com/radio.mp3
```

---

## 📖 Usage

### Streaming Steps

1. ✅ **Run the Application**
   ```bash
   python main.py
   ```

2. ✅ **Open Browser**
   ```
   http://localhost:8000
   ```

3. ✅ **Select Station**
   - Choose radio station from the list
   - Click the stream button

4. ✅ **Start Streaming**
   - Streaming will automatically start to Telegram
   - Monitor stream status from the interface

### User Interface

- 📊 **Dashboard** - View current stream status
- 🎛️ **Control** - Start/stop streaming
- 📡 **Stations** - List of available stations
- 📈 **Statistics** - Streaming statistics

---

## 📁 Project Structure

```
quran-stream/
├── 📂 templates/              # HTML templates
│   └── index.html            # Main page
├── 📄 main.py                # Main code
├── 📄 mp3quran_radios.m3u    # Radio stations list
├── 📄 requirements.txt       # Requirements
├── 🐳 Dockerfile             # Docker file
└── 📄 Procfile              # Deployment file
```

---

## 🛠️ Technologies Used

<div align="center">

| Technology | Description |
|------------|-------------|
| ![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white) | Main programming language |
| ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi&logoColor=white) | Web framework |
| ![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?logo=ffmpeg&logoColor=white) | Audio/video processing |
| ![RTMP](https://img.shields.io/badge/RTMP-Protocol-FF6B6B?logo=rtmp&logoColor=white) | Live streaming protocol |
| ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white) | Containers |

</div>

---

## 🚀 Deployment

### Render.com

The project is ready for deployment on Render.com. See `render.yaml` for settings.

### Heroku

Use the existing `Procfile` for Heroku deployment.

---

## 🤝 Contributing

Contributions are welcome! 🎉

1. 🍴 Fork the project
2. 🌿 Create a branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push (`git push origin feature/AmazingFeature`)
5. 🔄 Open a Pull Request

---

## ⚠️ Important Notes

- ⚖️ Make sure you have proper permission to use Quranic radio content
- 🔒 Protect your connection information
- 📊 Monitor bandwidth usage

---

## 📄 License

This project is open source and available for free use.

---

## 📞 Contact & Support

- 🐛 **Report Issues**: [Open an Issue](https://github.com/3bkader-gpt/quran-stream/issues)
- 💡 **Suggest Features**: [Open an Issue](https://github.com/3bkader-gpt/quran-stream/issues)
- 📧 **Email**: medo.omar.salama@gmail.com

---

<div align="center">

**Made with ❤️ by [Mohamed Omar](https://github.com/3bkader-gpt)**

⭐ If you like this project, don't forget to give it a star!

[⬆ Back to Top](#-quran-stream)

</div>