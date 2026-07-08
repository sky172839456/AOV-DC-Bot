from datetime import datetime


def _now():
    return datetime.now().strftime("%H:%M:%S")


def line():
    print("=" * 60)


def info(message):
    print(f"[{_now()}] [INFO] {message}")


def success(message):
    print(f"[{_now()}] [ OK ] {message}")


def warning(message):
    print(f"[{_now()}] [WARN] {message}")


def error(message):
    print(f"[{_now()}] [ERROR] {message}")