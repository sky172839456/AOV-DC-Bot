import unittest

from sources.aov_news import parse_detail_sections


class AovNewsDetailTests(unittest.TestCase):
    def test_extracts_purple_section_titles(self):
        html = """
        <div id="news_content">
          <p>一般前言，不應成為標題。</p>
          <p style="text-align:center">
            <span style="color:rgb(153, 102, 255)"><strong>英雄調整</strong></span>
          </p>
          <p>英雄調整的詳細內容。</p>
          <p><span style="color:#9966ff"><strong>BUG 修復</strong></span></p>
        </div>
        """
        self.assertEqual(parse_detail_sections(html), ["英雄調整", "BUG 修復"])

    def test_deduplicates_and_limits_sections(self):
        rows = "".join(
            f'<p><span style="color:#9966ff"><strong>章節 {index}</strong></span></p>'
            for index in range(10)
        )
        html = f'<div id="news_content">{rows}{rows}</div>'
        sections = parse_detail_sections(html)
        self.assertEqual(len(sections), 8)
        self.assertEqual(sections[0], "章節 0")
        self.assertEqual(sections[-1], "章節 7")


if __name__ == "__main__":
    unittest.main()
