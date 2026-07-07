import requests


def send_discord(webhook_url, news):

    embed = {
        "title": "📢 傳說對決最新公告",
        "description": f"**{news['title']}**",
        "url": news["url"],
        "color": 3447003,
        "fields": [
            {
                "name": "🏷 類別",
                "value": news["category"],
                "inline": True
            },
            {
                "name": "📅 日期",
                "value": news["date"],
                "inline": True
            }
        ]
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