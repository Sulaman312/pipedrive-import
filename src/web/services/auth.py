"""Authentication policy independent from Flask route handlers."""

import hmac
import os


def is_configured() -> bool:
    return bool(os.getenv("APP_USERNAME") and os.getenv("APP_PASSWORD"))


def credentials_match(username: str, password: str) -> bool:
    return hmac.compare_digest(username, os.getenv("APP_USERNAME", "")) and hmac.compare_digest(
        password, os.getenv("APP_PASSWORD", "")
    )
