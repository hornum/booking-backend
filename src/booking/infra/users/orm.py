from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from booking.infra.db import Base
from booking.infra.token.orm import RefreshTokenOrm


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str]

    tokens: Mapped["RefreshTokenOrm"] = relationship(back_populates="user", cascade="all, delete-orphan")
