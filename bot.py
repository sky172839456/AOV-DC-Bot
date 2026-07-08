from config import WEBHOOK_URL
from sources.aov_news import fetch_latest_news
from core.storage import load_latest_id, save_latest_id
from core.discord_webhook import send_discord


def main():

    print("=" * 50)
    print("AOV Discord Bot")
    print("=" * 50)

    news_list = fetch_latest_news()

    if not news_list:
        print("找不到任何公告")
        return

    latest_id = load_latest_id()

    print(f"目前紀錄：{latest_id}")

    new_news = []

    # 找出所有尚未通知的公告
    for news in news_list:

        if news["id"] == latest_id:
            break

        new_news.append(news)

    if not new_news:
        print("沒有新公告")
        return

    if not WEBHOOK_URL:
        raise Exception("WEBHOOK_URL 尚未設定")

    print(f"共有 {len(new_news)} 篇新公告")

    # 依照發布順序（舊 → 新）發送
    for news in reversed(new_news):

        print("-" * 50)
        print(f"發送：{news['title']}")
        print(news["date"])
        print(news["url"])

        send_discord(
            WEBHOOK_URL,
            news
        )

    # 更新最新公告 ID
    save_latest_id(news_list[0]["id"])

    print("-" * 50)
    print("全部公告發送完成！")


if __name__ == "__main__":
    main()