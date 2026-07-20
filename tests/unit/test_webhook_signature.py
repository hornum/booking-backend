from booking.infra.payment.webhook_signature import verify_payment_signature


def test_signature_create_verify_success(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=webhook_signature_data.body,
        secret=webhook_signature_data.secret,
        timestamp=webhook_signature_data.timestamp,
        signature=webhook_signature_data.signature,
    )
    assert signature_is_valid


def test_signature_changed_body_failure(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=b"fail_test_body",
        secret=webhook_signature_data.secret,
        timestamp=webhook_signature_data.timestamp,
        signature=webhook_signature_data.signature,
    )
    assert not signature_is_valid


def test_signature_invalid_timestamp_fail(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=webhook_signature_data.body,
        secret=webhook_signature_data.secret,
        timestamp=10,
        signature=webhook_signature_data.signature,
    )
    assert not signature_is_valid


def test_signature_invalid_secret_fail(webhook_signature_data):
    signature_is_valid = verify_payment_signature(
        body=webhook_signature_data.body,
        secret="wrong_secret",
        timestamp=webhook_signature_data.timestamp,
        signature=webhook_signature_data.signature,
    )
    assert not signature_is_valid
