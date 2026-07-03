from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from booking.infra.db import Base
from booking.infra.users.orm import UserORM


class RefreshTokenOrm(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    expires_at: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(DateTime(), server_default=func.now())
    revoked_at: Mapped[datetime] = mapped_column(DateTime(), nullable=True)

    user: Mapped["UserORM"] = relationship(back_populates="tokens")
