from datetime import datetime

import pytest
from pydantic import ValidationError

from booking.api.schemas.booking import BookRoomRequest
from booking.domain.bookings.errors import (
    InvalidBookingTime,
    InvalidStatusTransition,
    SlotTaken,
)
from booking.domain.bookings.models import Booking, BookingStatus
from booking.service.booking import book_room
from tests.fakes import FakeBookingRepository


def test_start_after_end_error():
    with pytest.raises(InvalidBookingTime):
        Booking(
            room_id=1,
            user_id=1,
            start=datetime(2026, 1, 1, 9, 30),
            end=datetime(2026, 1, 1, 8, 30),
            status=BookingStatus.HOLD,
        )


def test_request_rejects_end_before_start():
    with pytest.raises(ValidationError):
        BookRoomRequest(
            start=datetime(2026, 1, 1, 10, 0),
            end=datetime(2026, 1, 1, 9, 0),
        )


@pytest.mark.asyncio
async def test_overlapping_error():
    repo = FakeBookingRepository()

    await book_room(
        repo=repo,
        user_id=1,
        room_id=1,
        start=datetime(2026, 1, 1, 9, 0),
        end=datetime(2026, 1, 1, 10, 0),
    )

    with pytest.raises(SlotTaken):
        await book_room(
            repo=repo,
            user_id=1,
            room_id=1,
            start=datetime(2026, 1, 1, 9, 30),
            end=datetime(2026, 1, 1, 10, 30),
        )


def test_hold_can_be_confirmed(base_booking_data: dict):
    booking = Booking(**base_booking_data)
    booking.change_status(BookingStatus.CONFIRMED)
    assert booking.status == BookingStatus.CONFIRMED


def test_confirmed_can_be_cancelled(base_booking_data: dict):
    booking = Booking(**base_booking_data)
    booking.change_status(BookingStatus.CONFIRMED)
    booking.change_status(BookingStatus.CANCELLED)
    assert booking.status == BookingStatus.CANCELLED


def test_hold_to_hold_change(base_booking_data: dict):
    booking = Booking(**base_booking_data)
    with pytest.raises(InvalidStatusTransition):
        booking.change_status(BookingStatus.HOLD)


def test_canceled_cant_be_confirmed(base_booking_data: dict):
    booking = Booking(**base_booking_data)
    booking.change_status(BookingStatus.CANCELLED)
    with pytest.raises(InvalidStatusTransition):
        booking.change_status(BookingStatus.CONFIRMED)


def test_expired_cant_be_confirmed(base_booking_data: dict):
    booking = Booking(**base_booking_data)
    booking.change_status(BookingStatus.EXPIRED)
    with pytest.raises(InvalidStatusTransition):
        booking.change_status(BookingStatus.CONFIRMED)


def test_direct_status_assignment_forbidden(base_booking_data: dict):
    booking = Booking(**base_booking_data)
    with pytest.raises(AttributeError):
        booking.status = BookingStatus.CONFIRMED
