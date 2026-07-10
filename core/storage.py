from pathlib import Path

LATEST_FILE = Path("latest.txt")
SENT_IDS_FILE = Path("sent_ids.txt")
MAX_SENT_IDS = 500


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
    儲存最新公告 ID。
    使用暫存檔再 replace，避免寫入中斷時留下半個 latest.txt。
    """

    temp_file = LATEST_FILE.with_suffix(".tmp")

    temp_file.write_text(
        str(news_id),
        encoding="utf-8"
    )

    temp_file.replace(LATEST_FILE)


def load_sent_ids():
    if not SENT_IDS_FILE.exists():
        return set()

    return {
        line.strip()
        for line in SENT_IDS_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def save_sent_ids(news_ids):
    """保存最近已成功發送的文章 ID，避免跨分類或排序變動造成重送。"""

    unique_ids = list(dict.fromkeys(str(news_id) for news_id in news_ids))
    unique_ids = unique_ids[-MAX_SENT_IDS:]
    temp_file = SENT_IDS_FILE.with_suffix(".tmp")
    temp_file.write_text("\n".join(unique_ids), encoding="utf-8")
    temp_file.replace(SENT_IDS_FILE)
