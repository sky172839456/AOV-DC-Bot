import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import AOV_NEWS_URL

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_latest_news():
    """
    抓取 AOV 官方最新公告
    回傳:
        {
            id,
            title,
            date,
            datetime,
            url,
            image,
            category
        }
    """

    response = requests.get(
        AOV_NEWS_URL,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    news_list = []

    # 取得所有公告
    events = soup.select("div.event")

    current_year = datetime.now().year

    for event in events:

        # =====================
        # 標題
        # =====================

        title_tag = event.select_one(".event_title")

        if title_tag is None:
            continue

        title = title_tag.get_text(strip=True)

        # =====================
        # 日期
        # =====================

        date_tag = event.select_one(".event_date")

        if date_tag is None:
            continue

        date_text = date_tag.get_text(strip=True)

        try:
            dt = datetime.strptime(
                f"{current_year}/{date_text}",
                "%Y/%m/%d"
            )
        except:
            continue

        # =====================
        # 連結
        # =====================

        link = event.select_one("a")

        if link is None:
            continue

        href = link.get("href", "")

        if href.startswith("/"):
            url = "https://moba.garena.tw" + href
        else:
            url = href

        # =====================
        # ID
        # =====================

        news_id = url.rstrip("/").split("/")[-1]

        # =====================
        # 圖片
        # =====================

        image = None

        img = event.select_one("img")

        if img:
            image = img.get("src")

        # =====================
        # 類別
        # =====================

        category = "公告"

        icon = event.select_one(".event_list_icon")

        if icon:
            category = icon.get_text(strip=True)

        # =====================

        news_list.append({

            "id": news_id,

            "title": title,

            "date": date_text,

            "datetime": dt,

            "url": url,

            "image": image,

            "category": category

        })

    # =====================
    # 排序
    # =====================

    news_list.sort(
        key=lambda x: x["datetime"],
        reverse=True
    )

    if not news_list:
        return None

    return news_list[0]