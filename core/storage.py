from pathlib import Path

LATEST_FILE = Path("latest.txt")


def load_latest_id():
    """
    讀取上次通知的公告 ID
    """

    if not LATEST_FILE.exists():
        return None

    text = LATEST_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if text == "":
        return None

    return text


def save_latest_id(news_id):
    """
    儲存最新公告 ID
    """

    LATEST_FILE.write_text(
        str(news_id),
        encoding="utf-8"
    )