from booking.domain.bookings.repo import BookingRepository
from booking.domain.users.errors import UserNotFound
from booking.domain.users.models import User
from booking.domain.users.repo import UserRepository


async def admin_change_user_status(
    user_repo: UserRepository,
    booking_repo: BookingRepository,
    new_status: bool,
    target_user_id: int,
) -> User:
    user = await user_repo.get(target_user_id)

    if user is None:
        raise UserNotFound()
    if new_status is False:
        await booking_repo.cancel_all_by_user_id(target_user_id)
    user.is_active = new_status
    return await user_repo.update(user)


async def admin_get_user(
    repo: UserRepository,
    target_user_id: int,
) -> User:
    user = await repo.get(target_user_id)
    if user is None:
        raise UserNotFound()
    return user


async def admin_get_users(
    repo: UserRepository,
    offset: int,
    limit: int,
) -> list[User]:
    return await repo.get_all(offset=offset, limit=limit)
