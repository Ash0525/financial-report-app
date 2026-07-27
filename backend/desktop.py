import threading, time, urllib.request, uvicorn, webview
from backend.main import app

# Restrict server to this computer
HOST = "127.0.0.1"

# Identifies where the local server listens
PORT = 8000

# Address displayed inside the desktop window
APP_URL = f"http://{HOST}:{PORT}"