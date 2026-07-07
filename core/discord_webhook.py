import requests
from datetime import datetime


def send_discord(webhook_url, news):

    embed = {
        "title": "📢 傳說對決｜最新公告",

        "description": f"## 📌 {news['title']}",

        "url": news["url"],

        # Discord 藍色
        "color": 0x3498DB,

        "fields": [

            {
                "name": "🏷️ 類別",
                "value": news["category"],
                "inline": True
            },

            {
                "name": "📅 日期",
                "value": news["date"],
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

    if news["image"]:
        embed["image"] = {
            "url": news["image"]
        }

    payload = {
        "embeds": [embed]
    }

    response = requests.post(
        webhook_url,
        json=payload,
        timeout=15
    )

    response.raise_for_status()