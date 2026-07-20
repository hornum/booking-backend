from booking.domain.bookings.errors import BookingNotFound, BookingNotPayable
from booking.domain.bookings.models import BookingStatus
from booking.domain.bookings.repo import BookingRepository
from booking.domain.payment.errors import PaymentNotFound
from booking.domain.payment.models import Payment, PaymentStatus
from booking.domain.payment.provider import PaymentProvider, PaymentSession
from booking.domain.payment.repo import PaymentRepository
from booking.service.booking import _get_owned_booking


async def start_payment(
    booking_repo: BookingRepository,
    payment_repo: PaymentRepository,
    provider: PaymentProvider,
    booking_id: int,
    actor_id: int,
) -> PaymentSession:
    booking = await _get_owned_booking(
        repo=booking_repo, actor_id=actor_id, booking_id=booking_id
    )

    if booking.status != BookingStatus.HOLD:
        raise BookingNotPayable()

    # TODO: Real amount count
    amount = 50000

    pay_session = await provider.create_session(amount=amount, booking_id=booking_id)
    payment = Payment(
        booking_id=booking_id,
        amount=amount,
        provider_session_id=pay_session.session_id,
        status=PaymentStatus.PENDING,
    )
    await payment_repo.add(payment)

    return pay_session


async def handle_payment_webhook(
    payment_repo: PaymentRepository,
    booking_repo: BookingRepository,
    session_id: str,
    succeeded: bool,
) -> None:
    payment = await payment_repo.get_by_session_id(session_id)
    if payment is None:
        raise PaymentNotFound("Payment not found")
    if payment.status != PaymentStatus.PENDING:
        return

    if succeeded:
        booking = await booking_repo.get(payment.booking_id)
        if booking is None:
            raise BookingNotFound("Booking not found")

        payment.change_status(PaymentStatus.SUCCEEDED)
        booking.change_status(BookingStatus.CONFIRMED)
        await booking_repo.update(booking)
    else:
        payment.change_status(PaymentStatus.FAILED)

    await payment_repo.update(payment)
