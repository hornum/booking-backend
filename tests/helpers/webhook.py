import json
import time
from dataclasses import dataclass

from booking.infra.payment.webhook_signature import create_webhook_signature


@dataclass(frozen=True)
class SignedWebhook:
    body: bytes
    headers: dict[str, str]


def make_signed_webhook(
    *,
    session_id: str,
    succeeded: bool,
    secret: str,
) -> SignedWebhook:
    body = json.dumps(
        {
            "session_id": session_id,
            "succeeded": succeeded,
        },
        separators=(",", ":"),
    ).encode()

    timestamp = int(time.time())

    signature = create_webhook_signature(
        body=body,
        timestamp=timestamp,
        secret=secret,
    )

    return SignedWebhook(
        body=body,
        headers={
            "Content-Type": "application/json",
            "X-Signature": signature,
            "X-Timestamp": str(timestamp),
        },
    )
