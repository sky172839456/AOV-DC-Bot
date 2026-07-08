import os
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# Discord Webhook（正式）
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Discord Webhook（測試）
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL")

# 傳說對決公告首頁
AOV_NEWS_URL = "https://moba.garena.tw/news/"