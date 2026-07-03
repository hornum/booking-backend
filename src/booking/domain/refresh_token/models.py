from dataclasses import dataclass
from datetime import datetime


@dataclass
class RefreshToken:
    token_hash: str
    user_id: int
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None = None
    id: int | None = None
