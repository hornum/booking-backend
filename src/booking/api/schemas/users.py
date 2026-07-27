from datetime import datetime

from pydantic import BaseModel

from booking.domain.users.models import UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime


class AdminUserResponse(UserResponse):
    role: UserRole
    is_active: bool
