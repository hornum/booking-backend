from datetime import datetime

from booking.domain.bookings.errors import (
    BookingAccessDenied,
    BookingNotFound,
    SlotTaken,
)
from booking.domain.bookings.models import Booking, BookingStatus
from booking.domain.bookings.repo import BookingRepository
from booking.domain.users.errors import UserNotFound
from booking.domain.users.repo import UserRepository
from booking.infra.filters import BookingFilter


async def _get_owned_booking(
    repo: BookingRepository, actor_id: int, booking_id: int
) -> Booking:
    booking = await repo.get(booking_id)
    if booking is None:
        raise BookingNotFound()
    if actor_id != booking.user_id:
        raise BookingAccessDenied()
    return booking


async def book_room(
    repo: BookingRepository, user_id: int, room_id: int, start: datetime, end: datetime
) -> Booking:
    overlapping = await repo.find_overlapping(room_id, start, end)
    if overlapping:
        raise SlotTaken()

    booking = Booking(
        room_id=room_id,
        user_id=user_id,
        start=start,
        end=end,
        status=BookingStatus.HOLD,
    )

    return await repo.add(booking)


async def confirm_booking(
    repo: BookingRepository, booking_id: int, actor_id: int
) -> Booking:
    booking = await _get_owned_booking(
        repo=repo, actor_id=actor_id, booking_id=booking_id
    )
    booking.change_status(BookingStatus.CONFIRMED)
    return await repo.update(booking)


async def cancel_booking(
    repo: BookingRepository, booking_id: int, actor_id: int
) -> Booking:
    booking = await _get_owned_booking(
        repo=repo, actor_id=actor_id, booking_id=booking_id
    )
    booking.change_status(BookingStatus.CANCELLED)
    return await repo.update(booking)


async def get_booking(
    repo: BookingRepository, booking_id: int, actor_id: int
) -> Booking:
    booking = await _get_owned_booking(
        repo=repo, actor_id=actor_id, booking_id=booking_id
    )
    return booking


async def user_get_bookings(
    repo: BookingRepository,
    actor_id: int,
    room_id: int | None,
    offset: int,
    limit: int,
) -> list[Booking]:
    return await repo.get_all(
        filters=BookingFilter(user_id=actor_id, room_id=room_id),
        offset=offset,
        limit=limit,
    )


async def admin_confirm_booking(repo: BookingRepository, booking_id: int) -> Booking:
    booking = await repo.get(booking_id=booking_id)
    if booking is None:
        raise BookingNotFound()
    booking.change_status(BookingStatus.CONFIRMED)
    return await repo.update(booking)


async def admin_cancel_booking(repo: BookingRepository, booking_id: int) -> Booking:
    booking = await repo.get(booking_id=booking_id)
    if booking is None:
        raise BookingNotFound()
    booking.change_status(BookingStatus.CANCELLED)
    return await repo.update(booking)


async def admin_create_booking(
    user_repo: UserRepository,
    booking_repo: BookingRepository,
    target_user_id: int,
    room_id: int,
    start: datetime,
    end: datetime,
    create_confirmed: bool = True,
) -> Booking:
    user = await user_repo.get(target_user_id)
    if user is None:
        raise UserNotFound()

    booking_status = BookingStatus.CONFIRMED if create_confirmed else BookingStatus.HOLD

    overlapping = await booking_repo.find_overlapping(room_id, start, end)
    if overlapping:
        raise SlotTaken()

    booking = Booking(
        room_id=room_id,
        user_id=target_user_id,
        start=start,
        end=end,
        status=booking_status,
    )

    return await booking_repo.add(booking)


async def admin_get_bookings(
    booking_repo: BookingRepository,
    user_repo: UserRepository,
    offset: int,
    limit: int,
    target_user_id: int | None = None,
) -> list[Booking]:
    if target_user_id is not None:
        user = await user_repo.get(target_user_id)
        if user is None:
            raise UserNotFound()
    return await booking_repo.get_all(
        filters=BookingFilter(user_id=target_user_id),
        offset=offset,
        limit=limit,
    )
