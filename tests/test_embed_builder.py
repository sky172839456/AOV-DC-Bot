import unittest
from datetime import datetime, timezone

from embeds.embed_builder import build_embed


class EmbedBuilderTests(unittest.TestCase):
    def test_shows_official_date_and_taipei_discovery_time(self):
        news = {
            "title": "測試公告",
            "date": "07/16",
            "category": "公告",
            "url": "https://moba.garena.tw/news/show/1",
            "discovered_at": datetime(2026, 7, 14, 3, 23, tzinfo=timezone.utc),
        }
        description = build_embed(news)["description"]
        self.assertIn("官網標示日期", description)
        self.assertIn("07/16", description)
        self.assertIn("機器人發現時間（台灣時間）", description)
        self.assertIn("07/14 11:23", description)

    def test_test_card_labels_time_as_test_execution(self):
        news = {
            "title": "測試公告", "date": "07/18", "category": "活動",
            "url": "https://moba.garena.tw/news/show/1", "is_test": True,
            "discovered_at": datetime(2026, 7, 20, 5, 15, tzinfo=timezone.utc),
        }
        description = build_embed(news)["description"]
        self.assertIn("測試執行時間（台灣時間）", description)
        self.assertNotIn("機器人發現時間（台灣時間）", description)
        self.assertIn("07/20 13:15", description)


if __name__ == "__main__":
    unittest.main()
