import requests

from core.retry import retry
from core.logger import send, success, error

from embeds.embed_builder import build_embed


@retry(
    retries=3,
    delay=2
)
def send_discord(webhook_url, news):
    """
    發送 Discord Webhook
    """

    embed = build_embed(news)

    payload = {
        "embeds": [embed],

        "components": [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "style": 5,
                        "label": "📖 官方公告",
                        "url": news["url"]
                    }
                ]
            }
        ]
    }

    send(f"Discord：{news['title']}")

    try:

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=20
        )

        if response.status_code >= 400:

            print()
            print("=" * 60)

            error("Discord 回傳錯誤")
            error(f"Status : {response.status_code}")
            error(response.text)

            print()
            print("========== Payload ==========")
            print(payload)
            print("=============================")
            print()

        response.raise_for_status()

        success("Discord 發送成功")

        return True

    except requests.exceptions.RequestException as e:

        print()
        print("=" * 60)

        error("Discord Webhook 發送失敗")
        error(str(e))
        print("=" * 60)
        print()

        return False