"""
AOV Discord BOT
Retry Utility
"""

import time
from functools import wraps

from core.logger import warning


def retry(
    retries=3,
    delay=2,
    backoff=2,
    exceptions=(Exception,)
):
    """
    Retry Decorator

    retries:
        最大重試次數

    delay:
        第一次等待秒數

    backoff:
        每次等待倍數
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            current_delay = delay

            for attempt in range(1, retries + 1):

                try:
                    return func(*args, **kwargs)

                except exceptions as e:

                    if attempt == retries:
                        raise

                    warning(
                        f"{func.__name__}() 失敗 "
                        f"({attempt}/{retries}) "
                        f"→ {e}"
                    )

                    warning(
                        f"{current_delay} 秒後重新嘗試..."
                    )

                    time.sleep(current_delay)

                    current_delay *= backoff

        return wrapper

    return decorator