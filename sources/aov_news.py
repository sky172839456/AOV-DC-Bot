import requests
from bs4 import BeautifulSoup
from datetime import datetime

from config import AOV_NEWS_URL
from core.retry import retry
from core.logger import fetch, success


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_page(page):
    """
    抓取指定頁數
    """

    if page == 1:
        url = AOV_NEWS_URL
    else:
        url = f"{AOV_NEWS_URL}?page={page}"

    fetch(f"連線 Garena 第 {page} 頁")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    return response.text

def parse_events(html):
    """
    解析單一頁公告
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    news_list = []

    current_year = datetime.now().year

    events = soup.select("div.event")

    for index, event in enumerate(events):

        title_tag = event.select_one(".event_list_title")
        if title_tag is None:
            continue

        title = title_tag.get_text(strip=True)

        date_tag = event.select_one(".event_list_date")
        if date_tag is None:
            continue

        date_text = date_tag.get_text(strip=True)

        try:

            dt = datetime.strptime(
                f"{current_year}/{date_text}",
                "%Y/%m/%d"
            )

        except Exception:
            continue

        link = event.select_one("a")

        if link is None:
            continue

        href = link.get("href", "")

        if href.startswith("/"):
            url = "https://moba.garena.tw" + href
        else:
            url = href

        news_id = url.rstrip("/").split("/")[-1]

        image = None

        img = event.select_one("img")

        if img:

            image = img.get("src")

            if image and image.startswith("/"):
                image = "https://moba.garena.tw" + image

        category = "公告"

        icon = event.select_one(".event_list_icon")

        if icon:
            category = icon.get_text(strip=True)

        news_list.append({

            "id": news_id,

            "title": title,

            "date": date_text,

            "datetime": dt,

            "url": url,

            "image": image,

            "category": category,

            "order": index

        })

    return news_list

@retry()
def fetch_latest_news():
    """
    抓取 AOV 官方所有公告
    """
    raise Exception("我是新的 fetch_latest_news()")
    fetch("連線 Garena 官方網站")

    news_list = []

    for page in [1, 2]:

        print("=" * 40)
        print(f"DEBUG：開始抓第 {page} 頁")

        html = fetch_page(page)

        print(f"DEBUG：第 {page} 頁抓取完成")

        if page == 1:
            with open("garena.html", "w", encoding="utf-8") as f:
                f.write(html)

        count = len(parse_events(html))
        print(f"DEBUG：第 {page} 頁解析到 {count} 則公告")

        news_list.extend(
            parse_events(html)
        )

        print(f"DEBUG：目前總共 {len(news_list)} 則公告")

    news_list.sort(
        key=lambda x: (
            x["datetime"],
            -x["order"]
        ),
        reverse=True
    )

    success(f"成功抓到 {len(news_list)} 則公告")

    return news_list