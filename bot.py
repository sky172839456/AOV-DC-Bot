from config import WEBHOOK_URL
from sources.aov_news import fetch_latest_news
from core.storage import load_latest_id, save_latest_id
from core.discord_webhook import send_discord


def main():

    print("=" * 50)
    print("AOV Discord Bot")
    print("=" * 50)

    news = fetch_latest_news()

    if news is None:
        print("找不到任何公告")
        return

    print("最新公告：")
    print(news["title"])
    print(news["date"])
    print(news["url"])

    latest_id = load_latest_id()

    print(f"目前紀錄：{latest_id}")
    print(f"最新公告：{news['id']}")

    if latest_id == news["id"]:
        print("沒有新公告")
        return

    if not WEBHOOK_URL:
        raise Exception("WEBHOOK_URL 尚未設定")

    print("發送 Discord...")

    send_discord(
        WEBHOOK_URL,
        news
    )

    save_latest_id(news["id"])

    print("完成！")


if __name__ == "__main__":
    main()