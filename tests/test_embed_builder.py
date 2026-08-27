import unittest
from datetime import datetime, timezone

from embeds.embed_builder import build_embed
from sources.aov_news import normalize_image_url, parse_detail_image


class EmbedBuilderTests(unittest.TestCase):
    def test_image_url_spaces_are_encoded_for_discord(self):
        image = normalize_image_url(
            "https://dlgarenanow-a.akamaihd.net/mgames/kgtw/Official website/2022/hot fix676.jpg"
        )
        self.assertEqual(
            image,
            "https://dlgarenanow-a.akamaihd.net/mgames/kgtw/Official%20website/2022/hot%20fix676.jpg",
        )
        self.assertNotIn(" ", image)

    def test_detail_image_fallback_is_also_encoded(self):
        image = parse_detail_image(
            '<div class="news_content"><img src="/images/event banner.jpg"></div>',
            "https://moba.garena.tw/news/show/1",
        )
        self.assertEqual(image, "https://moba.garena.tw/images/event%20banner.jpg")

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

    def test_shows_detail_section_titles_before_link(self):
        news = {
            "title": "不停機更新公告",
            "date": "08/27",
            "category": "公告",
            "url": "https://moba.garena.tw/news/show/1",
            "sections": ["英雄平衡性調整", "BUG 修復"],
        }
        description = build_embed(news)["description"]
        self.assertIn("本次更新重點", description)
        self.assertIn("• 英雄平衡性調整", description)
        self.assertIn("• BUG 修復", description)
        self.assertLess(description.index("本次更新重點"), description.index("公告連結"))


if __name__ == "__main__":
    unittest.main()
