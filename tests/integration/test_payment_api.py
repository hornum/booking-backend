import json
import time

from booking.domain.payment.models import PaymentStatus
from booking.infra.payment.repository import SqlPaymentRepository
from booking.infra.payment.webhook_signature import create_webhook_signature
from tests.helpers.webhook import make_signed_webhook


async def test_pay_create_and_conf_api(auth_client, webhook_secret, pending_payment):
    webhook = make_signed_webhook(
        session_id=pending_payment.session_id,
        succeeded=True,
        secret=webhook_secret,
    )

    response = await auth_client.post(
        "/v1/payments/webhook",
        content=webhook.body,
        headers=webhook.headers,
    )
    assert response.status_code == 200

    get = await auth_client.get(f"/v1/bookings/{pending_payment.booking_id}")
    assert get.status_code == 200
    assert get.json()["status"] == "confirmed"


async def test_webhook_idempotent(auth_client, webhook_secret, pending_payment):
    webhook = make_signed_webhook(
        session_id=pending_payment.session_id,
        succeeded=True,
        secret=webhook_secret,
    )
    for _ in range(2):
        response = await auth_client.post(
            "/v1/payments/webhook",
            content=webhook.body,
            headers=webhook.headers,
        )
        assert response.status_code == 200

        get = await auth_client.get(f"/v1/bookings/{pending_payment.booking_id}")
        assert get.status_code == 200
        assert get.json()["status"] == "confirmed"


async def test_unknown_session_webhook_fail(client, webhook_secret):
    body = json.dumps(
        {"session_id": "test", "succeeded": True},
        separators=(",", ":"),
    ).encode()
    timestamp = int(time.time())
    webhook_signature = create_webhook_signature(
        body=body,
        timestamp=timestamp,
        secret=webhook_secret,
    )
    response = await client.post(
        "/v1/payments/webhook",
        content=body,
        headers={"X-Signature": webhook_signature, "X-Timestamp": str(timestamp)},
    )
    assert response.status_code == 404


async def test_webhook_failed_payment(
    auth_client, webhook_secret, pending_payment, session
):
    webhook = make_signed_webhook(
        session_id=pending_payment.session_id,
        succeeded=False,
        secret=webhook_secret,
    )

    response = await auth_client.post(
        "/v1/payments/webhook",
        content=webhook.body,
        headers=webhook.headers,
    )
    assert response.status_code == 200

    get = await auth_client.get(f"/v1/bookings/{pending_payment.booking_id}")
    assert get.status_code == 200
    assert get.json()["status"] == "hold"

    payment_repo = SqlPaymentRepository(session=session)
    payment = await payment_repo.get_by_session_id(pending_payment.session_id)
    assert payment.status == PaymentStatus.FAILED


async def test_webhook_without_signature_fail(
    auth_client, webhook_secret, pending_payment
):
    webhook = make_signed_webhook(
        session_id=pending_payment.session_id,
        succeeded=True,
        secret=webhook_secret,
    )

    response = await auth_client.post(
        "/v1/payments/webhook",
        content=webhook.body,
        headers={"X-Timestamp": str(int(time.time()))},
    )
    assert response.status_code == 422


async def test_invalid_signature_fail(auth_client, webhook_secret, pending_payment):
    webhook = make_signed_webhook(
        session_id=pending_payment.session_id,
        succeeded=True,
        secret=webhook_secret,
    )

    response = await auth_client.post(
        "/v1/payments/webhook",
        content=webhook.body,
        headers={"X-Signature": "fail", "X-Timestamp": str(int(time.time()))},
    )
    assert response.status_code == 401
