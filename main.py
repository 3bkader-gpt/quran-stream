from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import threading
import os
import logging
import queue
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

# Paths
BASE_DIR = Path(__file__).parent
M3U_PATH = BASE_DIR / "mp3quran_radios.m3u"
TEMPLATES_DIR = BASE_DIR / "templates"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="QuranStream Local Controller")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Global stream queue for HTTP server
stream_queue = queue.Queue(maxsize=100)
stream_lock = threading.Lock()


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP Server with threading support"""
    daemon_threads = True


class StreamHTTPHandler(BaseHTTPRequestHandler):
    """HTTP Handler that serves stream data from queue"""
    
    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')  # MP3 format
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()
            
            logger.info("Client connected to stream endpoint")
            try:
                while True:
                    try:
                        # Get data from queue with timeout
                        chunk = stream_queue.get(timeout=2)
                        if chunk is None:  # Sentinel value to stop
                            break
                        if chunk:  # Only send non-empty chunks
                            self.wfile.write(chunk)
                            self.wfile.flush()
                    except queue.Empty:
                        # Keep connection alive - FFmpeg will wait for data
                        # Send a small keep-alive chunk if needed
                        try:
                            self.wfile.write(b'')
                            self.wfile.flush()
                        except:
                            break
                        time.sleep(0.1)
                        continue
                    except (BrokenPipeError, ConnectionResetError):
                        logger.info("Client disconnected")
                        break
            except Exception as e:
                logger.error(f"Error serving stream: {e}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass


# HTTP Server instance
http_server: Optional[ThreadingHTTPServer] = None
http_server_thread: Optional[threading.Thread] = None


def slug_to_name(slug: str) -> str:
    # Normalize slug to a human-friendly name
    s = slug.strip().replace("-", " ")
    s = s.replace("_", " ")
    s = " ".join(part for part in s.split() if part)
    # Fix common double underscores that become double spaces
    s = " ".join([p for p in s.split(" ") if p])
    # Title case the string
    name = s.title()
    # Minor fixes for common words (optional)
    replacements = {
        "Al": "Al",
        "Ibn": "Ibn",
        "Bin": "Bin",
        "An": "An",
    }
    name_parts = name.split()
    name_parts = [replacements.get(p, p) for p in name_parts]
    return " ".join(name_parts)


def parse_m3u(content: str) -> List[Dict[str, str]]:
    stations: List[Dict[str, str]] = []
    seen = set()
    for line in content.splitlines():
        url = line.strip()
        if not url:
            continue
        if url.startswith("#"):
            # Ignore metadata lines (not present in this file, but safe)
            continue
        if url in seen:
            continue
        seen.add(url)
        # Extract slug from URL path
        name = url
        try:
            # Take last path segment after '/'
            slug = url.rstrip('/').split('/')[-1]
            name = slug_to_name(slug)
        except Exception:
            # Fallback
            name = url
        stations.append({"id": len(stations) + 1, "name": name, "url": url})
    return stations


class _Singleton(type):
    _instances: Dict[type, object] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
            return cls._instances[cls]


class StreamManager(metaclass=_Singleton):
    def __init__(self) -> None:
        self._main_process: Optional[subprocess.Popen] = None  # Main FFmpeg that streams to RTMP
        self._feed_process: Optional[subprocess.Popen] = None  # Feed process that reads from source
        self._lock = threading.Lock()
        self._current_station: Optional[Dict[str, str]] = None
        self._rtmp_url: Optional[str] = None
        self._http_port = 8888

    def _build_rtmp_url(self, server: str, key: str) -> str:
        server = server.strip()
        key = key.strip()
        if not server:
            return key
        if server.endswith('/'):
            return f"{server}{key}"
        return f"{server}/{key}"

    def _start_http_server(self):
        """Start HTTP server if not already running"""
        global http_server, http_server_thread
        
        if http_server is not None:
            return
        
        try:
            http_server = ThreadingHTTPServer(('127.0.0.1', self._http_port), StreamHTTPHandler)
            http_server_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
            http_server_thread.start()
            logger.info(f"HTTP Server started on port {self._http_port}")
        except Exception as e:
            logger.error(f"Failed to start HTTP server: {e}")

    def _start_main_stream(self, rtmp_url: str) -> bool:
        """Start main FFmpeg process that reads from stdin pipe and streams to RTMP"""
        if self._main_process and self._main_process.poll() is None:
            # Already running, just update RTMP URL if different
            if self._rtmp_url != rtmp_url:
                logger.warning("RTMP URL changed but main stream is running. Restarting...")
                self.stop_stream()
            else:
                return True
        
        # Main FFmpeg reads from stdin pipe and streams to RTMP
        cmd = [
            "ffmpeg",
            "-loglevel", "error",
            "-nostats",
            "-f", "s16le",  # Input format: raw PCM
            "-ar", "44100",  # Sample rate
            "-ac", "2",  # Channels
            "-i", "pipe:0",  # Read from stdin
            "-vn",
            "-c:a", "aac",
            "-b:a", "128k",
            "-flags", "+low_delay",
            "-fflags", "nobuffer",
            "-f", "flv",
            rtmp_url,
        ]
        
        try:
            self._main_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,  # Accept input from stdin
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )
            self._rtmp_url = rtmp_url
            logger.info(f"Main FFmpeg process started with PID: {self._main_process.pid}")
            
            # Monitor main process and log errors
            def monitor_main():
                try:
                    # Read stderr to see errors
                    error_lines = []
                    def read_stderr():
                        try:
                            for line in self._main_process.stderr:
                                line_str = line.decode('utf-8', errors='ignore').strip()
                                if line_str:
                                    error_lines.append(line_str)
                                    if 'error' in line_str.lower() or 'failed' in line_str.lower():
                                        logger.error(f"Main FFmpeg: {line_str}")
                        except Exception as e:
                            logger.error(f"Error reading main stderr: {e}")
                    
                    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                    stderr_thread.start()
                    
                    exit_code = self._main_process.wait()
                    if exit_code != 0:
                        logger.error(f"Main FFmpeg process exited with code {exit_code}")
                        if error_lines:
                            logger.error(f"Last errors: {error_lines[-5:]}")
                    else:
                        logger.warning("Main FFmpeg process exited normally")
                except Exception as e:
                    logger.error(f"Error monitoring main process: {e}")
            
            threading.Thread(target=monitor_main, daemon=True).start()
            return True
        except FileNotFoundError:
            logger.error("FFmpeg not found in PATH")
            return False
        except Exception as e:
            logger.error(f"Failed to start main FFmpeg: {e}")
            return False

    def _feed_stream(self, stream_url: str, station_name: Optional[str] = None):
        """Feed stream data to main FFmpeg stdin via queue"""
        if not self._main_process or self._main_process.poll() is not None:
            logger.error("Main process not running, cannot feed stream")
            return None
        
        cmd = [
            "ffmpeg",
            "-loglevel", "error",
            "-nostats",
            "-re",
            "-reconnect", "1",
            "-reconnect_at_eof", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "2",
            "-i", stream_url,
            "-vn",
            "-c:a", "pcm_s16le",  # Raw PCM 16-bit little-endian
            "-ar", "44100",
            "-ac", "2",
            "-f", "s16le",  # Raw PCM format
            "-",  # Output to stdout
        ]
        
        try:
            feed_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,  # Read from stdout
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            )
            
            logger.info(f"Feed process started for {station_name} with PID: {feed_proc.pid}")
            
            # Write from feed to main process stdin in a separate thread
            def write_to_main():
                try:
                    chunk_size = 8192
                    while True:
                        chunk = feed_proc.stdout.read(chunk_size)
                        if not chunk:
                            break
                        try:
                            if self._main_process and self._main_process.poll() is None and self._main_process.stdin:
                                self._main_process.stdin.write(chunk)
                                self._main_process.stdin.flush()
                            else:
                                logger.warning("Main process stdin not available")
                                break
                        except (BrokenPipeError, OSError) as e:
                            logger.error(f"Error writing to main stdin: {e}")
                            break
                except Exception as e:
                    logger.error(f"Error in write_to_main: {e}")
                finally:
                    logger.info(f"Feed write thread ended for {station_name}")
            
            write_thread = threading.Thread(target=write_to_main, daemon=True)
            write_thread.start()
            
            # Monitor feed process
            def monitor_feed():
                try:
                    error_lines = []
                    def read_stderr():
                        try:
                            for line in feed_proc.stderr:
                                line_str = line.decode('utf-8', errors='ignore').strip()
                                if line_str:
                                    error_lines.append(line_str)
                                    if 'error' in line_str.lower() or 'failed' in line_str.lower():
                                        logger.error(f"Feed FFmpeg error: {line_str}")
                        except Exception as e:
                            logger.error(f"Error reading feed stderr: {e}")
                    
                    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
                    stderr_thread.start()
                    
                    exit_code = feed_proc.wait()
                    if exit_code != 0:
                        logger.warning(f"Feed process exited with code {exit_code}")
                        if error_lines:
                            logger.error(f"Last errors: {error_lines[-3:]}")
                    else:
                        logger.info(f"Feed process ended normally for {station_name}")
                except Exception as e:
                    logger.error(f"Error monitoring feed process: {e}")
            
            threading.Thread(target=monitor_feed, daemon=True).start()
            return feed_proc
        except Exception as e:
            logger.error(f"Failed to start feed process: {e}")
            return None

    def start_stream(self, stream_url: str, rtmp_server: str, stream_key: str, station_name: Optional[str] = None) -> Dict[str, str]:
        with self._lock:
            logger.info(f"Starting stream - Station: {station_name}, URL: {stream_url}")
            logger.info(f"RTMP Server: {rtmp_server}, Key: {stream_key[:10]}...")
            
            rtmp_url = self._build_rtmp_url(rtmp_server, stream_key)
            logger.info(f"Full RTMP URL: {rtmp_url[:50]}...")
            
            # Clean up any dead processes first
            if self._feed_process and self._feed_process.poll() is not None:
                self._feed_process = None
            if self._main_process and self._main_process.poll() is not None:
                self._main_process = None
            
            # Stop ALL old processes first (both feed and main if RTMP URL changed)
            if self._feed_process and self._feed_process.poll() is None:
                logger.info(f"Stopping old feed process (PID: {self._feed_process.pid})")
                try:
                    self._feed_process.kill()  # Force kill for faster stop
                    try:
                        self._feed_process.wait(timeout=1)
                    except:
                        pass
                except Exception as e:
                    logger.error(f"Error stopping feed: {e}")
                self._feed_process = None
            
            # If RTMP URL changed, restart main process too
            if self._main_process and self._main_process.poll() is None:
                if self._rtmp_url != rtmp_url:
                    logger.info(f"RTMP URL changed, restarting main process (PID: {self._main_process.pid})")
                    try:
                        self._main_process.kill()
                        try:
                            self._main_process.wait(timeout=1)
                        except:
                            pass
                    except Exception as e:
                        logger.error(f"Error stopping main process: {e}")
                    self._main_process = None
                    self._rtmp_url = None
            
            # Small delay to ensure old processes are fully stopped
            time.sleep(0.3)
            
            # Kill ALL FFmpeg processes as safety measure (Windows only)
            # This ensures no orphaned processes interfere
            if os.name == 'nt':
                try:
                    # Use taskkill to kill all ffmpeg processes
                    kill_proc = subprocess.Popen(
                        ['taskkill', '/F', '/IM', 'ffmpeg.exe'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    kill_proc.wait(timeout=2)
                    if kill_proc.returncode == 0:
                        logger.info("Killed all FFmpeg processes as safety measure")
                    time.sleep(0.5)  # Wait for processes to fully terminate
                except subprocess.TimeoutExpired:
                    kill_proc.kill()
                except Exception as e:
                    logger.debug(f"Could not clean up orphaned processes: {e}")
            
            # Start or ensure main stream is running
            if not self._start_main_stream(rtmp_url):
                return {"error": "failed to start main stream"}
            
            # Start feeding new stream
            self._feed_process = self._feed_stream(stream_url, station_name)
            
            if not self._feed_process:
                return {"error": "failed to start feed process"}
            
            self._current_station = {"name": station_name or stream_url, "url": stream_url}
            
            return {"status": "starting", "rtmp": rtmp_url}

    def stop_stream(self) -> Dict[str, str]:
        with self._lock:
            # Stop feed process (force kill for speed)
            if self._feed_process and self._feed_process.poll() is None:
                logger.info(f"Stopping feed process (PID: {self._feed_process.pid})")
                try:
                    self._feed_process.kill()  # Force kill
                    try:
                        self._feed_process.wait(timeout=1)
                    except:
                        pass
                except Exception as e:
                    logger.error(f"Error stopping feed: {e}")
            
            # Stop main process (force kill for speed)
            if self._main_process and self._main_process.poll() is None:
                logger.info(f"Stopping main stream (PID: {self._main_process.pid})")
                try:
                    self._main_process.kill()  # Force kill
                    try:
                        self._main_process.wait(timeout=1)
                        logger.info("Main stream stopped")
                    except:
                        pass
                except Exception as e:
                    logger.error(f"Error stopping main stream: {e}")
            
            # Close stdin if open
            if self._main_process and self._main_process.stdin:
                try:
                    self._main_process.stdin.close()
                except:
                    pass
            
            self._main_process = None
            self._feed_process = None
            self._current_station = None
            
            # Kill all FFmpeg processes as final cleanup (Windows only)
            if os.name == 'nt':
                try:
                    subprocess.Popen(
                        ['taskkill', '/F', '/IM', 'ffmpeg.exe'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    ).wait(timeout=2)
                except:
                    pass
            
            return {"status": "stopped"}

    def get_status(self) -> Dict[str, Optional[str]]:
        with self._lock:
            # Stream is running if main process is running (feed can restart without stopping stream)
            running = self._main_process is not None and self._main_process.poll() is None
            name = self._current_station.get("name") if self._current_station else None
            url = self._current_station.get("url") if self._current_station else None
            feed_running = self._feed_process is not None and self._feed_process.poll() is None
            return {"running": running, "name": name, "url": url, "feed_running": feed_running}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Render template
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/stations")
async def get_stations():
    try:
        content = M3U_PATH.read_text(encoding="utf-8")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to read M3U file: {e}"})
    stations = parse_m3u(content)
    return stations


@app.post("/api/start")
async def api_start(payload: Dict[str, str]):
    url = payload.get("url")
    rtmp_server = payload.get("rtmp_server", "")
    key = payload.get("key", "")
    if not url or not rtmp_server or not key:
        return JSONResponse(status_code=400, content={"error": "Missing url, rtmp_server, or key"})

    # Find station name by URL (optional)
    station_name: Optional[str] = None
    try:
        content = M3U_PATH.read_text(encoding="utf-8")
        stations = parse_m3u(content)
        match = next((s for s in stations if s["url"] == url), None)
        station_name = match["name"] if match else None
    except Exception:
        station_name = None

    # Run in thread to avoid blocking
    import asyncio
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, StreamManager().start_stream, url, rtmp_server, key, station_name)
    if "error" in result:
        return JSONResponse(status_code=500, content=result)
    return result


@app.post("/api/stop")
async def api_stop():
    result = StreamManager().stop_stream()
    return result


@app.get("/api/status")
async def api_status():
    status = StreamManager().get_status()
    return status


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down, stopping streams...")
    StreamManager().stop_stream()
    
    # Shutdown HTTP server
    global http_server
    if http_server:
        http_server.shutdown()
        logger.info("HTTP Server stopped")
