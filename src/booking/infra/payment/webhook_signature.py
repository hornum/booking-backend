import hashlib
import hmac
import time

from config.config import settings


def create_webhook_signature(
    body: bytes,
    timestamp: int,
    secret: str,
) -> str:
    signed_payload = str(timestamp).encode() + b"." + body

    signature = hmac.new(
        key=secret.encode(), msg=signed_payload, digestmod=hashlib.sha256
    ).hexdigest()

    return signature


def verify_payment_signature(
    *,
    body: bytes,
    timestamp: int,
    signature: str,
    secret: str,
    max_age_seconds: int = settings.DEFAULT_MAX_AGE_SECONDS,
    curr_timestamp: int | None = None,
) -> bool:

    if curr_timestamp is None:
        curr_timestamp = int(time.time())

    if curr_timestamp - timestamp > max_age_seconds:
        return False
    if timestamp - curr_timestamp > settings.MAX_FUTURE_SKEW_SECONDS:
        return False

    expected_signature = create_webhook_signature(
        body=body,
        timestamp=timestamp,
        secret=secret,
    )

    return hmac.compare_digest(expected_signature, signature)
