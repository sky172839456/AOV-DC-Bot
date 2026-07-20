import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from config import (
    WEBHOOK_URL,
    TEST_WEBHOOK_URL
)

from sources.aov_news import (fetch_latest_news, fill_missing_images)

from core.storage import (
    load_latest_id,
    save_latest_id,
    load_sent_ids,
    save_sent_ids
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


TAIPEI = ZoneInfo("Asia/Taipei")


def collect_new_news(news_list, latest_id, sent_ids=None, force_mode=False):
    """
    回傳這次需要發送的公告。
    news_list 需由新到舊排序。
    """

    if force_mode:
        return news_list[:1]

    new_news = []
    seen_ids = set(sent_ids or ())

    for news in news_list:
        if news["id"] == latest_id:
            break

        if news["id"] in seen_ids:
            continue

        seen_ids.add(news["id"])
        new_news.append(news)

    return new_news


def collect_category_samples(news_list):
    """挑選最新一則公告與活動，供測試頻道驗證分類抓取。"""

    samples = []
    for category in ("公告", "活動"):
        sample = next(
            (news for news in news_list if category in news.get("category", "")),
            None
        )
        if sample:
            samples.append(sample)

    return samples


def send_news_list(webhook_url, new_news):
    """
    依時間由舊到新發送公告。
    遇到第一個失敗就停止，避免 newer 公告先發而 older 公告漏發。
    """

    success_count = 0
    last_successful_id = None
    failed_news = None

    for news in reversed(new_news):
        if send_discord(webhook_url, news):
            success_count += 1
            last_successful_id = news["id"]
            continue

        failed_news = news
        warning(f"公告發送失敗，停止後續發送：{news.get('title', news['id'])}")
        break

    return success_count, last_successful_id, failed_news


def main():

    # -----------------------------
    # Command Line Arguments
    # -----------------------------

    force_mode = "--force" in sys.argv
    test_mode = "--test" in sys.argv
    test_categories_mode = "--test-categories" in sys.argv

    if test_categories_mode:
        test_mode = True

    # -----------------------------
    # Banner
    # -----------------------------

    banner()

    info("BOT 啟動")

    if force_mode:
        warning("Force Mode：ON（忽略 latest.txt，只送最新一篇）")

    if test_mode:
        warning("Test Mode：使用測試 Webhook")

    # -----------------------------
    # Fetch News
    # -----------------------------

    news_list = fetch_latest_news()

    if not news_list:
        warning("找不到任何公告")
        done("Finished")
        return 1

    latest_id = load_latest_id()
    sent_ids = load_sent_ids()

    info(f"目前 latest.txt：{latest_id}")

    if test_categories_mode:
        new_news = collect_category_samples(news_list)
        found_categories = {news.get("category") for news in new_news}
        if len(new_news) != 2:
            warning(f"分類測試失敗，無法同時找到公告與活動：{found_categories}")
            done("Finished")
            return 1
        info("分類測試：將發送最新公告與最新活動各一則")
    else:
        new_news = collect_new_news(
            news_list,
            latest_id,
            sent_ids=sent_ids,
            force_mode=force_mode
        )

    if not new_news:
        info("沒有新公告")
        done("Finished")
        return 0

    info(f"共有 {len(new_news)} 則新公告")

    discovered_at = datetime.now(TAIPEI)
    for news in new_news:
        news["discovered_at"] = discovered_at

    fill_missing_images(new_news)

    # -----------------------------
    # Select Webhook
    # -----------------------------

    webhook_url = TEST_WEBHOOK_URL if test_mode else WEBHOOK_URL

    if not webhook_url:
        warning("未設定 Webhook，無法發送 Discord 公告")
        done("Finished")
        return 1

    # -----------------------------
    # Send Discord
    # -----------------------------

    success_count, last_successful_id, failed_news = send_news_list(
        webhook_url,
        new_news
    )

    # -----------------------------
    # Save latest.txt
    # -----------------------------

    if test_categories_mode:
        info("分類測試：不更新 latest.txt 與 sent_ids.txt")
        if failed_news:
            warning(f"分類測試發送失敗（{success_count}/{len(new_news)}）")
            done("Finished")
            return 1
        success(f"分類測試發送完成（{success_count}/{len(new_news)}）")
        done("Finished")
        return 0

    if force_mode:
        info("Force Mode：不更新 latest.txt")

        if failed_news:
            warning(f"Force Mode 發送失敗（{success_count}/{len(new_news)}）")
            done("Finished")
            return 1

        success(f"Force Mode 發送完成（{success_count}/{len(new_news)}）")
        done("Finished")
        return 0

    if last_successful_id:
        save("更新 latest.txt")
        save_latest_id(last_successful_id)
        successful_ids = [
            news["id"]
            for news in reversed(new_news)
        ][:success_count]
        save_sent_ids([*sent_ids, *successful_ids])

    if failed_news:
        warning(
            "部分公告發送失敗，latest.txt 只更新到最後一則成功發送的公告 "
            f"（{success_count}/{len(new_news)}）"
        )
        done("Finished")
        return 1

    success(f"全部公告發送完成（{success_count}/{len(new_news)}）")
    done("Finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())
