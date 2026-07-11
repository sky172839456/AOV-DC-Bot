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
NEWS_SOURCES = (
    ("公告", AOV_NEWS_URL),
    ("活動", urljoin(AOV_NEWS_URL, "Activity")),
)


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


def fetch_url(url: str) -> str:
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()
    response.encoding = "utf-8"

    return response.text


def fetch_page(base_url: str, page: int) -> str:
    """
    抓取指定頁面的 HTML
    """

    if page == 1:
        url = base_url
    else:
        url = f"{base_url}?page={page}"

    fetch(f"連線 Garena 第 {page} 頁")

    return fetch_url(url)


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


def normalize_image_url(image_src):
    if not image_src:
        return None

    image = urljoin(BASE_URL, image_src)

    if not image.startswith("http"):
        return None

    return image


def find_list_image(event):
    img = event.select_one("img")

    if not img:
        return None

    return normalize_image_url(
        img.get("src")
        or img.get("data-src")
        or img.get("data-original")
    )


def parse_detail_image(html: str, page_url: str):
    """
    從公告內頁抓圖片。優先使用社群分享圖 og:image。
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    selectors = [
        "meta[property='og:image']",
        "meta[name='twitter:image']"
    ]

    for selector in selectors:
        meta = soup.select_one(selector)
        image = normalize_image_url(meta.get("content") if meta else None)

        if image:
            return image

    img = soup.select_one("article img, .news_content img, .content img, img")

    if not img:
        return None

    image_src = (
        img.get("src")
        or img.get("data-src")
        or img.get("data-original")
    )

    if not image_src:
        return None

    return urljoin(page_url, image_src)


def fetch_detail_image(news):
    """
    列表沒有圖片時，進公告內頁補抓圖片。
    """

    try:
        fetch(f"抓取公告圖片：{news['id']}")
        html = fetch_url(news["url"])
        return parse_detail_image(html, news["url"])
    except requests.RequestException as exc:
        warning(f"公告圖片抓取失敗：{news['id']} → {exc}")
        return None


def parse_events(html: str, default_category="公告"):
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

        # 官網同一頁同時有一般列表與置頂大卡片，兩者使用不同 class。
        title_tag = event.select_one(".event_list_title, .event_title_text")
        if not title_tag:
            continue

        date_tag = event.select_one(".event_list_date, .event_date")
        if not date_tag:
            continue

        link_tag = event.select_one("a[href*='/news/show/']")
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

        category = default_category
        icon = event.select_one(".event_list_icon")

        if icon:
            category = icon.get_text(strip=True) or category

        news_list.append({
            "id": news_id,
            "title": title,
            "date": date_text,
            "datetime": dt,
            "url": url,
            "image": find_list_image(event),
            "category": category,
            "order": index
        })

    return news_list


def fill_missing_images(news_list):
    for news in news_list:
        if news.get("image"):
            continue

        news["image"] = fetch_detail_image(news)

    return news_list


@retry()
def fetch_latest_news():
    """
    抓取 AOV 官方公告
    """

    fetch("連線 Garena 官方網站")

    news_list = []
    news_by_id = {}
    max_pages = get_max_pages()

    for source_category, source_url in NEWS_SOURCES:
        for page in range(1, max_pages + 1):
            html = fetch_page(source_url, page)
            info(f"Garena {source_category}第 {page} 頁 HTML 長度：{len(html)}")

            if source_category == "公告" and page == 1 and should_save_debug_html():
                with open(
                    "garena.html",
                    "w",
                    encoding="utf-8"
                ) as f:
                    f.write(html)

            page_news = parse_events(html, default_category=source_category)

            if not page_news:
                warning(f"{source_category}第 {page} 頁沒有解析到內容，停止抓取")
                break

            added_count = 0

            for news in page_news:
                existing = news_by_id.get(news["id"])
                if existing:
                    # 同一篇可能同時出現在公告與活動頁；只保留一筆，
                    # 但只要活動頁有收錄，就以「活動」作為分類。
                    if source_category == "活動":
                        existing["category"] = "活動"
                    continue

                news_by_id[news["id"]] = news
                news_list.append(news)
                added_count += 1

            info(f"{source_category}第 {page} 頁新增 {added_count} 則內容")

    news_list.sort(
        key=lambda x: (
            x["datetime"],
            -x["order"]
        ),
        reverse=True
    )

    success(f"成功抓到 {len(news_list)} 則公告")

    return news_list
