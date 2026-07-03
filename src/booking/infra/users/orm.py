from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from booking.infra.db import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str]
