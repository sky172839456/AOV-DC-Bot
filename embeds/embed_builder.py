from datetime import datetime

from embeds.colors import get_color
from embeds.icons import get_embed_icon


BOT_NAME = "🤖 AOV 情報雷達"
BOT_VERSION = "2.5.0"
OFFICIAL_SITE_URL = "https://moba.garena.tw/"
OFFICIAL_FACEBOOK_URL = "https://www.facebook.com/AoVTW/"


def build_embed(news):
    """
    建立 Discord Embed
    """

    icon = get_embed_icon(news)

    description = (
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"# 📌 {news['title']}\n\n"
        f"📅 **日期**\n"
        f"{news.get('date', '-')}\n\n"
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

        "timestamp": datetime.utcnow().isoformat()

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
