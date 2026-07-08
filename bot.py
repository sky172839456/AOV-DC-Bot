from config import WEBHOOK_URL
from sources.aov_news import fetch_latest_news
from core.storage import load_latest_id, save_latest_id
from core.discord_webhook import send_discord

from core.logger import (
    banner,
    info,
    fetch,
    send,
    save,
    success,
    warning,
    done
)


def main():

    banner()

    info("BOT 啟動")

    fetch("開始抓取 Garena 官方公告...")

    news_list = fetch_latest_news()

    if not news_list:
        warning("找不到任何公告")
        done()
        return

    success(f"成功取得 {len(news_list)} 則公告")

    latest_id = load_latest_id()

    info(f"目前 latest.txt：{latest_id}")

    new_news = []

    for news in news_list:

        if news["id"] == latest_id:
            break

        new_news.append(news)

    if not new_news:
        info("沒有新公告")
        done()
        return

    info(f"共有 {len(new_news)} 則新公告")

    # ============================
    # 開發模式（本機沒有 Webhook）
    # ============================

    if not WEBHOOK_URL:

        warning("未設定 WEBHOOK_URL")
        warning("已跳過 Discord 發送（開發模式）")

        done()

        return

    # ============================
    # 正式發送
    # ============================

    for news in reversed(new_news):

        print()

        send(f"Discord：{news['title']}")

        send_discord(
            WEBHOOK_URL,
            news
        )

    save("更新 latest.txt")

    save_latest_id(
        news_list[0]["id"]
    )

    success("全部公告發送完成")

    done()


if __name__ == "__main__":
    main()