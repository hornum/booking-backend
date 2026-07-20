from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from booking.api.dependencies import get_session
from booking.api.schemas.payment import WebhookPayload
from booking.domain.bookings.errors import BookingNotFound
from booking.domain.payment.errors import PaymentNotFound
from booking.infra.bookings.repository import SqlBookingRepository
from booking.infra.payment.repository import SqlPaymentRepository
from booking.infra.payment.webhook_signature import verify_payment_signature
from booking.service.payment import handle_payment_webhook
from config.config import settings

router = APIRouter(prefix="/v1/payments", tags=["Payment"])


@router.post("/webhook", status_code=200)
async def webhook(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    webhook_signature: Annotated[str, Header(alias="X-Signature")],
    timestamp_header: Annotated[str, Header(alias="X-Timestamp")],
) -> dict[str, bool]:
    try:
        timestamp = int(timestamp_header)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401, detail="Invalid payment signature"
        ) from None

    payment_repo = SqlPaymentRepository(session)
    booking_repo = SqlBookingRepository(session)

    raw_body = await request.body()

    signature_is_valid = verify_payment_signature(
        body=raw_body,
        timestamp=timestamp,
        signature=webhook_signature,
        secret=settings.PAYMENT_WEBHOOK_SECRET,
    )
    if not signature_is_valid:
        raise HTTPException(status_code=401, detail="Invalid payment signature")

    payload = WebhookPayload.model_validate_json(raw_body)

    try:
        await handle_payment_webhook(
            payment_repo=payment_repo,
            booking_repo=booking_repo,
            session_id=payload.session_id,
            succeeded=payload.succeeded,
        )

    except (PaymentNotFound, BookingNotFound) as error:
        raise HTTPException(status_code=404, detail=f"{error}") from None

    return {"ok": True}
