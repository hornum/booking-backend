from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from booking.api.dependencies import get_current_user
from booking.domain.users.models import User

router = APIRouter(prefix="/v1/user", tags=["User"])


@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
