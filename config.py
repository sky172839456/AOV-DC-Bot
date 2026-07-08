import os
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

# Discord Webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 傳說對決公告首頁
AOV_NEWS_URL = "https://moba.garena.tw/news/"