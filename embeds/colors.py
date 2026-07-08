# Discord Embed Colors

DEFAULT = 0x3498DB     # 藍色
EVENT = 0x2ECC71       # 綠色
UPDATE = 0x9B59B6      # 紫色
MAINTENANCE = 0xE74C3C # 紅色
SHOP = 0xF1C40F        # 金色


def get_color(category: str) -> int:
    """
    根據公告類別回傳 Discord Embed 顏色
    """

    if not category:
        return DEFAULT

    text = category.lower()

    if "維護" in text or "停機" in text:
        return MAINTENANCE

    if "活動" in text:
        return EVENT

    if "商城" in text:
        return SHOP

    if "更新" in text:
        return UPDATE

    return DEFAULT