import requests
from datetime import datetime


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
            "text": "🤖 AOV Discord Bot｜自動同步 Garena 官方公告"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    # ---------- 圖片 ----------
    image = news.get("image")

    if (
        image
        and image.startswith("http")
        and image.lower() != "none"
    ):
        embed["image"] = {
            "url": image
        }

    payload = {
        "embeds": [embed]
    }

    print("📤 Discord 發送中...")

    try:

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=20
        )

        if response.status_code >= 400:

            print("=" * 60)
            print("❌ Discord 回傳錯誤")
            print("Status :", response.status_code)
            print(response.text)
            print("=" * 60)

        response.raise_for_status()

        print("✅ Discord 發送成功")

    except requests.exceptions.RequestException as e:

        print("=" * 60)
        print("❌ Discord Webhook 發送失敗")
        print(e)
        print("=" * 60)

        raise