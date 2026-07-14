"""
AOV Discord BOT
Logger System
"""

from datetime import datetime
import sys

from core.version import BOT_NAME, VERSION


for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")


def _time():
    return datetime.now().strftime("%H:%M:%S")


def _log(level: str, message: str):
    print(f"[{_time()}] [{level:<7}] {message}")


def banner():
    print()
    print("═" * 60)
    print(f"🤖 {BOT_NAME}")
    print(f"📦 Version : {VERSION}")
    print("═" * 60)
    print()


def info(message):
    _log("INFO", message)


def fetch(message):
    _log("FETCH", message)


def send(message):
    _log("SEND", message)


def save(message):
    _log("SAVE", message)


def success(message):
    _log("SUCCESS", message)


def warning(message):
    _log("WARNING", message)


def error(message):
    _log("ERROR", message)


def done(message="Finished"):
    _log("DONE", message)
