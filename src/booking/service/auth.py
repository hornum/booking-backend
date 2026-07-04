import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from booking.domain.refresh_token.errors import TokenNotFound, TokenExpired
from booking.domain.refresh_token.models import RefreshToken
from booking.domain.refresh_token.repo import TokenRepository
from booking.domain.users.errors import UserAlreadyExists, UserNotFound, IncorrectPassword
from booking.domain.users.models import User
from booking.domain.users.repo import UserRepository
from booking.infra import a_security
from booking.infra.a_security import hash_password, hash_token

from config.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str

@dataclass
class AuthResult:
    user_id: int
    access_token: str
    refresh_token: str


@dataclass
class LoginResult:
    user_id: int
    access_token: str
    refresh_token: str


async def _issue_tokens(token_repo: TokenRepository, user_id: int) -> TokenPair:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    access = a_security.create_access_token(user_id=user_id, expire=expire)
    refresh = a_security.create_refresh_token()
    await token_repo.add(RefreshToken(
        token_hash=a_security.hash_token(refresh),
        user_id=user_id,
        expires_at=expire,
        created_at=datetime.now(timezone.utc),
    ))
    return TokenPair(access_token=access, refresh_token=refresh)


async def register_user(
        user_repo: UserRepository,
        token_repo: TokenRepository,
        username: str,
        email: str,
        password: str
) -> AuthResult:
    existing = await user_repo.find_existing(username=username, email=email)
    if existing:
        raise UserAlreadyExists()

    user = User(username=username, email=email, hashed_password=await hash_password(password))
    user = await user_repo.add(user)

    tokens = await _issue_tokens(token_repo=token_repo, user_id=user.id)

    return AuthResult(
        user_id=user.id,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token
    )


async def login_user(
        user_repo: UserRepository,
        token_repo: TokenRepository,
        username: str,
        password: str
) -> LoginResult:
    user = await user_repo.find_by_username(username)
    if not user:
         raise UserNotFound()
    if not await a_security.verify_password(password, user.hashed_password):
        raise IncorrectPassword()

    tokens = await _issue_tokens(token_repo, user.id)

    return LoginResult(
        user_id=user.id,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token
    )


async def refresh_tokens(token_repo: TokenRepository, refresh_token: str) -> LoginResult:
    token = await token_repo.get_by_hash(hash_token(refresh_token))

    if not token:
        raise TokenNotFound

    if token.expires_at < datetime.now(timezone.utc) or token.revoked_at is not None:
        raise TokenExpired

    user_id = token.user_id
    await token_repo.revoke(token)
    tokens = await _issue_tokens(token_repo, user_id)

    return LoginResult(
        user_id=user_id,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token
    )


async def logout_user(token_repo: TokenRepository, refresh_token: str) -> None:
    token = await token_repo.get_by_hash(hash_token(refresh_token))
    if not token:
        return
    await token_repo.revoke(token)
