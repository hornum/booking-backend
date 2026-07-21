from booking.infra.payment.webhook_signature import (
    create_webhook_signature,
    verify_payment_signature,
)
from config.config import settings


def test_signature_create_verify_success(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=webhook_signature_data.body,
        secret=webhook_signature_data.secret,
        timestamp=webhook_signature_data.timestamp,
        signature=webhook_signature_data.signature,
        curr_timestamp=webhook_signature_data.timestamp,
    )
    assert signature_is_valid


def test_signature_changed_body_failure(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=b"fail_test_body",
        secret=webhook_signature_data.secret,
        timestamp=webhook_signature_data.timestamp,
        curr_timestamp=webhook_signature_data.timestamp,
        signature=webhook_signature_data.signature,
    )
    assert not signature_is_valid


def test_signature_future_timestamp_fail(webhook_signature_data):
    current_timestamp = webhook_signature_data.timestamp
    future_timestamp = (
            current_timestamp
            + settings.MAX_FUTURE_SKEW_SECONDS
            + 1
    )

    future_signature = create_webhook_signature(
        body=webhook_signature_data.body,
        timestamp=future_timestamp,
        secret=webhook_signature_data.secret,
    )

    signature_is_valid = verify_payment_signature(
        body=webhook_signature_data.body,
        secret=webhook_signature_data.secret,
        timestamp=future_timestamp,
        curr_timestamp=current_timestamp,
        signature=future_signature,
    )

    assert not signature_is_valid


def test_signature_expired_timestamp_fail(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=webhook_signature_data.body,
        secret=webhook_signature_data.secret,
        timestamp=webhook_signature_data.timestamp,
        curr_timestamp=(
                webhook_signature_data.timestamp
                + settings.DEFAULT_MAX_AGE_SECONDS
                + 1
        ),
        signature=webhook_signature_data.signature,
    )
    assert not signature_is_valid


def test_signature_delayed_timestamp_success(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=webhook_signature_data.body,
        secret=webhook_signature_data.secret,
        timestamp=webhook_signature_data.timestamp,
        curr_timestamp=webhook_signature_data.timestamp + 100,
        signature=webhook_signature_data.signature,
    )
    assert signature_is_valid


def test_signature_invalid_secret_fail(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=webhook_signature_data.body,
        secret="wrong_secret",
        timestamp=webhook_signature_data.timestamp,
        curr_timestamp=webhook_signature_data.timestamp,
        signature=webhook_signature_data.signature,
    )
    assert not signature_is_valid
