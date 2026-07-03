from dataclasses import dataclass

from booking.domain.users.errors import InvalidUserEmail


@dataclass
class User:
    username: str
    email: str
    hashed_password: str
    id: int | None = None

    def __post_init__(self) -> None:
        if self.email == "" or "@" not in self.email:
            raise InvalidUserEmail()
