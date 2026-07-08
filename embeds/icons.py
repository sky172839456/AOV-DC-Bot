"""
Discord Embed Icon System
"""


DEFAULT = "📢"

MAINTENANCE = "🛠️"

EVENT = "🎉"

SHOP = "🛒"

UPDATE = "🚀"

HERO = "⚔️"

ESPORT = "🏆"

NOTICE = "📣"


def get_embed_icon(news):

    text = (
        f"{news.get('category','')} "
        f"{news.get('title','')}"
    ).lower()

    # 維護
    if any(k in text for k in [
        "維護",
        "停機",
        "不停機"
    ]):
        return MAINTENANCE

    # 活動
    if any(k in text for k in [
        "活動"
    ]):
        return EVENT

    # 商城
    if any(k in text for k in [
        "商城",
        "造型"
    ]):
        return SHOP

    # 英雄
    if any(k in text for k in [
        "英雄"
    ]):
        return HERO

    # 世界賽
    if any(k in text for k in [
        "apl",
        "awc",
        "世界賽"
    ]):
        return ESPORT

    # 更新
    if any(k in text for k in [
        "更新",
        "版本"
    ]):
        return UPDATE

    return DEFAULT