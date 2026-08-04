import unittest
from datetime import datetime, timedelta

from bot import collect_category_samples, collect_new_news
from sources.aov_news import MONITORED_CATEGORIES, NEWS_SOURCES


class NewsCollectionTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 8, 5, 12, 0)

    def item(self, news_id, days_ago, category="公告"):
        return {
            "id": str(news_id),
            "title": f"文章 {news_id}",
            "datetime": self.now - timedelta(days=days_ago),
            "category": category,
        }

    def test_all_official_news_categories_have_independent_sources(self):
        labels = {name for name, _ in NEWS_SOURCES}
        self.assertEqual(labels, {"全部", "活動", "系統", "賽事", "教學"})

    def test_backdated_unseen_article_after_latest_boundary_is_not_missed(self):
        items = [self.item("5700", 0), self.item("5699", 1), self.item("5650", 2)]
        result = collect_new_news(items, "5699", sent_ids={"5700"}, now=self.now)
        self.assertEqual([item["id"] for item in result], ["5650"])

    def test_old_historical_articles_are_not_replayed(self):
        result = collect_new_news([self.item("5650", 45)], "5700", sent_ids=set(), now=self.now)
        self.assertEqual(result, [])

    def test_old_pinned_article_with_month_day_only_is_not_replayed(self):
        items = [self.item("5700", 0), self.item("5400", 0)]
        result = collect_new_news(items, "5699", sent_ids={"5700"}, now=self.now)
        self.assertEqual(result, [])

    def test_category_preview_covers_every_monitored_category(self):
        items = [self.item(index, index, category) for index, category in enumerate(MONITORED_CATEGORIES)]
        samples = collect_category_samples(items)
        self.assertEqual({item["category"] for item in samples}, set(MONITORED_CATEGORIES))


if __name__ == "__main__":
    unittest.main()
