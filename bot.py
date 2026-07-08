import sys

from config import WEBHOOK_URL
from sources.aov_news import fetch_latest_news

from core.storage import (
    load_latest_id,
    save_latest_id
)

from core.discord_webhook import send_discord

from core.logger import (
    banner,
    info,
    warning,
    success,
    save,
    done
)


def main():

    force_mode = "--force" in sys.argv

    banner()

    info("BOT 啟動")

    if force_mode:
        warning("Force Mode：ON（忽略 latest.txt）")

    news_list = fetch_latest_news()

    if not news_list:
        warning("找不到任何公告")
        return

    latest_id = load_latest_id()

    info(f"目前 latest.txt：{latest_id}")

    new_news = []

    if force_mode:

        # 只送最新一篇
        new_news.append(news_list[0])

    else:

        for news in news_list:

            if news["id"] == latest_id:
                break

            new_news.append(news)

    if not new_news:

        info("沒有新公告")
        done("Finished")
        return

    info(f"共有 {len(new_news)} 則新公告")

    if not WEBHOOK_URL:

        warning("未設定 WEBHOOK_URL")
        warning("已跳過 Discord 發送（開發模式）")

        done("Finished")
        return

    success_count = 0

    for news in reversed(new_news):

        if send_discord(
            WEBHOOK_URL,
            news
        ):
            success_count += 1

    if not force_mode:

        save("更新 latest.txt")
        save_latest_id(news_list[0]["id"])

        success("全部公告發送完成")

    else:

        info("Force Mode：不更新 latest.txt")

    done("Finished")


if __name__ == "__main__":
    main()