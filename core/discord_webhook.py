import requests
from datetime import datetime

from core.retry import retry
from core.logger import send, success, error


@retry(
    retries=3,
    delay=2
)
def send_discord(webhook_url, news):
    """
    發送 Discord Webhook
    """

    embed = {
        "title": "📢 傳說對決｜最新公告",
        "description": f"## 📌 {news['title']}",
        "url": news["url"],
        "color": 0x3498DB,
        "fields": [
            {
                "name": "🏷️ 類別",
                "value": news.get("category", "公告"),
                "inline": True
            },
            {
                "name": "📅 日期",
                "value": news.get("date", "-"),
                "inline": True
            },
            {
                "name": "🔗 官方公告",
                "value": f"[點我前往公告]({news['url']})",
                "inline": False
            }
        ],
        "footer": {
            "text": "🤖 AOV Discord BOT v2.5"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    # -----------------------
    # Image
    # -----------------------

    image = news.get("image")

    if (
        image
        and isinstance(image, str)
        and image.startswith("http")
        and image.lower() != "none"
    ):
        embed["image"] = {
            "url": image
        }

    payload = {
        "embeds": [embed]
    }

    send(f"Discord：{news['title']}")

    try:

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=20
        )

        if response.status_code >= 400:

            print()
            print("=" * 60)
            error("Discord 回傳錯誤")
            error(f"Status : {response.status_code}")
            error(response.text)

            print()
            print("========== Payload ==========")
            print(payload)
            print("=============================")
            print()

        response.raise_for_status()

        success("Discord 發送成功")

        return True

    except requests.exceptions.RequestException as e:

        print()
        print("=" * 60)
        error("Discord Webhook 發送失敗")
        error(str(e))
        print("=" * 60)
        print()

        # 不讓整個 BOT 中止
        return False