import os
from datetime import datetime, timedelta
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import AOV_NEWS_URL
from core.retry import retry
from core.logger import fetch, info, success, warning


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    )
}

BASE_URL = "https://moba.garena.tw"
DEFAULT_MAX_PAGES = 8


def get_max_pages():
    """
    可用 AOV_MAX_PAGES 調整最多抓幾頁，預設 8 頁。
    """

    raw_value = os.getenv("AOV_MAX_PAGES")

    if not raw_value:
        return DEFAULT_MAX_PAGES

    try:
        max_pages = int(raw_value)
    except ValueError:
        warning(f"AOV_MAX_PAGES 不是有效數字，使用預設 {DEFAULT_MAX_PAGES}")
        return DEFAULT_MAX_PAGES

    return max(1, max_pages)


def should_save_debug_html():
    return os.getenv("SAVE_GARENA_HTML", "").lower() in {
        "1",
        "true",
        "yes",
        "on"
    }


def fetch_page(page: int) -> str:
    """
    抓取指定頁面的 HTML
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
    response.encoding = "utf-8"

    return response.text


def parse_news_date(date_text: str):
    """
    官網列表只提供月/日，跨年時避免把去年 12 月公告解析成未來日期。
    """

    now = datetime.now()

    parsed = datetime.strptime(
        f"{now.year}/{date_text}",
        "%Y/%m/%d"
    )

    if parsed > now + timedelta(days=1):
        parsed = parsed.replace(year=now.year - 1)

    return parsed


def parse_events(html: str):
    """
    解析單一頁公告
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    events = soup.select("div.event")

    news_list = []

    for index, event in enumerate(events):

        title_tag = event.select_one(".event_list_title")
        if not title_tag:
            continue

        date_tag = event.select_one(".event_list_date")
        if not date_tag:
            continue

        link_tag = event.select_one("a")
        if not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        date_text = date_tag.get_text(strip=True)

        try:
            dt = parse_news_date(date_text)
        except ValueError:
            warning(f"略過無法解析日期的公告：{date_text} / {title}")
            continue

        href = link_tag.get("href", "")
        url = urljoin(BASE_URL, href)
        news_id = url.rstrip("/").split("/")[-1]

        if not news_id:
            warning(f"略過缺少公告 ID 的公告：{title}")
            continue

        image = None
        img = event.select_one("img")

        if img:
            image_src = img.get("src")

            if image_src:
                image = urljoin(BASE_URL, image_src)

        category = "公告"
        icon = event.select_one(".event_list_icon")

        if icon:
            category = icon.get_text(strip=True) or category

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
    抓取 AOV 官方公告
    """

    fetch("連線 Garena 官方網站")

    news_list = []
    seen_ids = set()
    max_pages = get_max_pages()

    for page in range(1, max_pages + 1):
        html = fetch_page(page)
        info(f"Garena 第 {page} 頁 HTML 長度：{len(html)}")

        if page == 1 and should_save_debug_html():
            with open(
                "garena.html",
                "w",
                encoding="utf-8"
            ) as f:
                f.write(html)

        page_news = parse_events(html)

        if not page_news:
            warning(f"第 {page} 頁沒有解析到公告，停止抓取")
            break

        added_count = 0

        for news in page_news:
            if news["id"] in seen_ids:
                continue

            seen_ids.add(news["id"])
            news_list.append(news)
            added_count += 1

        info(f"第 {page} 頁新增 {added_count} 則公告")

    news_list.sort(
        key=lambda x: (
            x["datetime"],
            -x["order"]
        ),
        reverse=True
    )

    success(f"成功抓到 {len(news_list)} 則公告")

    return news_list
