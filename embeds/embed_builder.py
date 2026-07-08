from datetime import datetime

from embeds.colors import get_color
from embeds.icons import get_embed_icon


BOT_NAME = "🤖 AOV Discord BOT"
BOT_VERSION = "2.5.0"


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
        "💡 **AI 摘要（V3）**\n"
        "🚧 尚未啟用\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔗 **[官方公告]({news['url']})**"
    )

    embed = {

        "title": f"{icon} Garena《傳說對決》",

        "description": description,

        "url": news["url"],

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