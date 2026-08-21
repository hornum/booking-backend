import pytest

from booking.domain.bookings.models import Booking, BookingStatus
from booking.domain.users.errors import UserNotFound
from booking.domain.users.models import User
from booking.service.user import admin_change_user_status


async def test_admin_deactivate_user(fake_user_repo, fake_booking_repo, base_user_model_data):
    user = await fake_user_repo.add(User(**base_user_model_data))
    assert user.is_active

    deactivated_user = await admin_change_user_status(
        user_repo=fake_user_repo,
        booking_repo=fake_booking_repo,
        new_status=False,
        target_user_id=user.id,
    )
    assert not deactivated_user.is_active


async def test_admin_activate_user(fake_user_repo, fake_booking_repo, base_user_model_data):
    user = await fake_user_repo.add(User(**base_user_model_data, is_active=False))
    assert not user.is_active

    activated_user = await admin_change_user_status(
        user_repo=fake_user_repo,
        booking_repo=fake_booking_repo,
        new_status=True,
        target_user_id=user.id,
    )
    assert activated_user.is_active


async def test_admin_activate_user_not_found(
        fake_user_repo,
        fake_booking_repo,
):
    with pytest.raises(UserNotFound):
        await admin_change_user_status(
            user_repo=fake_user_repo,
            booking_repo=fake_booking_repo,
            new_status=True,
            target_user_id=1,
        )


async def test_deactivation_cancels_all_active_user_bookings(
        fake_user_repo,
        fake_booking_repo,
    base_user_model_data,
    base_booking_model_data,
):
    user = await fake_user_repo.add(User(**base_user_model_data))
    assert user.id is not None

    hold_booking = await fake_booking_repo.add(
        Booking(
            **{
                **base_booking_model_data,
                "user_id": user.id,
                "room_id": 1,
                "status": BookingStatus.HOLD,
            }
        )
    )
    confirmed_booking = await fake_booking_repo.add(
        Booking(
            **{
                **base_booking_model_data,
                "user_id": user.id,
                "room_id": 2,
                "status": BookingStatus.CONFIRMED,
            }
        )
    )
    already_cancelled_booking = await fake_booking_repo.add(
        Booking(
            **{
                **base_booking_model_data,
                "user_id": user.id,
                "room_id": 3,
                "status": BookingStatus.CANCELLED,
            }
        )
    )

    await admin_change_user_status(
        user_repo=fake_user_repo,
        booking_repo=fake_booking_repo,
        new_status=False,
        target_user_id=user.id,
    )

    updated_hold = await fake_booking_repo.get(hold_booking.id)
    updated_confirmed = await fake_booking_repo.get(confirmed_booking.id)
    updated_cancelled = await fake_booking_repo.get(already_cancelled_booking.id)

    assert updated_hold.status == BookingStatus.CANCELLED
    assert updated_confirmed.status == BookingStatus.CANCELLED
    assert updated_cancelled.status == BookingStatus.CANCELLED


async def test_deactivation_does_not_cancel_other_user_bookings(
        fake_user_repo,
        fake_booking_repo,
    base_user_model_data,
    base_booking_model_data,
):
    target_user = await fake_user_repo.add(User(**base_user_model_data))
    other_user = await fake_user_repo.add(
        User(
            **{
                **base_user_model_data,
                "username": "other-user",
                "email": "other-user@example.com",
            }
        )
    )

    assert target_user.id is not None
    assert other_user.id is not None

    target_booking = await fake_booking_repo.add(
        Booking(
            **{
                **base_booking_model_data,
                "user_id": target_user.id,
                "room_id": 1,
                "status": BookingStatus.CONFIRMED,
            }
        )
    )
    other_user_booking = await fake_booking_repo.add(
        Booking(
            **{
                **base_booking_model_data,
                "user_id": other_user.id,
                "room_id": 2,
                "status": BookingStatus.CONFIRMED,
            }
        )
    )

    await admin_change_user_status(
        user_repo=fake_user_repo,
        booking_repo=fake_booking_repo,
        new_status=False,
        target_user_id=target_user.id,
    )

    updated_target_booking = await fake_booking_repo.get(target_booking.id)
    updated_other_booking = await fake_booking_repo.get(other_user_booking.id)

    assert updated_target_booking.status == BookingStatus.CANCELLED
    assert updated_other_booking.status == BookingStatus.CONFIRMED


async def test_activation_does_not_change_bookings(
        fake_user_repo,
        fake_booking_repo,
    base_user_model_data,
    base_booking_model_data,
):
    user = await fake_user_repo.add(User(**base_user_model_data, is_active=False))

    booking_data = {
        **base_booking_model_data,
        "status": BookingStatus.CANCELLED,
        "user_id": user.id,
    }
    booking = await fake_booking_repo.add(Booking(**booking_data))
    await admin_change_user_status(
        user_repo=fake_user_repo,
        booking_repo=fake_booking_repo,
        new_status=True,
        target_user_id=user.id,
    )
    updated_booking = await fake_booking_repo.get(booking.id)
    assert updated_booking.status == BookingStatus.CANCELLED
