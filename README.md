# QuranStream - Live Audio Streaming to Telegram

مشروع بث مباشر للراديو القرآني إلى Telegram عبر RTMP مع إمكانية تبديل القنوات بدون انقطاع.

## المميزات

- 🎵 بث مباشر بدون انقطاع (Zero Downtime)
- 🔄 تبديل القنوات بدون إيقاف البث
- 📻 126 محطة راديو قرآنية
- 🌐 واجهة ويب سهلة الاستخدام
- ⚡ أداء عالي مع معالجة متقدمة للعمليات

## المتطلبات

- Python 3.9+
- FFmpeg
- FastAPI
- Uvicorn

## التثبيت

```bash
# Clone المشروع
git clone https://github.com/YOUR_USERNAME/quran-stream.git
cd quran-stream

# تثبيت المتطلبات
pip install -r requirements.txt
```

## التشغيل

```bash
# Windows
uvicorn main:app --host 127.0.0.1 --port 8000

# Linux
uvicorn main:app --host 0.0.0.0 --port 8000
```

## الاستخدام

1. افتح المتصفح على `http://localhost:8000`
2. أدخل RTMP Server URL و Stream Key
3. اختر محطة من القائمة واضغط Play
4. للتبديل بين المحطات: اختر محطة جديدة - سيتم التبديل تلقائياً بدون انقطاع

## البنية

- `main.py` - الكود الرئيسي (FastAPI + Stream Manager)
- `mp3quran_radios.m3u` - قائمة المحطات (126 محطة)
- `templates/index.html` - الواجهة الأمامية
- `requirements.txt` - المتطلبات

## التقنيات المستخدمة

- **FastAPI** - Web Framework
- **FFmpeg** - Audio Streaming
- **Python Threading** - Process Management
- **Raw PCM Piping** - Zero Downtime Switching

## الرخصة

MIT License
