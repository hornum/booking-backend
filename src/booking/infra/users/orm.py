from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from booking.domain.users.models import UserRole
from booking.infra.db import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[UserRole] = mapped_column(String(16), server_default=UserRole.USER)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    username: Mapped[str]
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str]
