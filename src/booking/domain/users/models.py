from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from booking.domain.users.errors import InvalidUserEmail


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class User:
    username: str
    email: str
    hashed_password: str
    role: UserRole | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    id: int | None = None

    def __post_init__(self) -> None:
        if self.email == "" or "@" not in self.email:
            raise InvalidUserEmail()
