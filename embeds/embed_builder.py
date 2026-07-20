from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from embeds.colors import get_color
from embeds.icons import get_embed_icon


BOT_NAME = "🤖 AOV 情報雷達"
BOT_VERSION = "2.5.0"
OFFICIAL_SITE_URL = "https://moba.garena.tw/"
OFFICIAL_FACEBOOK_URL = "https://www.facebook.com/AoVTW/"
TAIPEI = ZoneInfo("Asia/Taipei")


def format_discovered_at(value):
    if not isinstance(value, datetime):
        return "-"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(TAIPEI).strftime("%m/%d %H:%M")


def build_embed(news):
    """
    建立 Discord Embed
    """

    icon = get_embed_icon(news)
    time_label = "測試執行時間（台灣時間）" if news.get("is_test") else "機器人發現時間（台灣時間）"

    description = (
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"# 📌 {news['title']}\n\n"
        f"📅 **官網標示日期**\n"
        f"{news.get('date', '-')}\n\n"
        f"🔎 **{time_label}**\n"
        f"{format_discovered_at(news.get('discovered_at'))}\n\n"
        f"🏷️ **類別**\n"
        f"{news.get('category', '公告')}\n\n"
        f"🔗 **公告連結：** <{news['url']}>\n"
        f"🌐 **官方網站：** <{OFFICIAL_SITE_URL}>\n"
        f"📘 **官方 FB：** <{OFFICIAL_FACEBOOK_URL}>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    embed = {

        "title": f"{icon} Garena《傳說對決》",

        "description": description,

        # 自動顏色
        "color": get_color(news.get("category", "")),

        "footer": {
            "text": (
                f"{BOT_NAME}\n"
                f"Version {BOT_VERSION}"
            )
        },

        "timestamp": datetime.now(timezone.utc).isoformat()

    }

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

    return embed
