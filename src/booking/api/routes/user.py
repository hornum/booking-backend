from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from booking.api.dependencies import get_current_user
from booking.api.schemas.users import UserResponse
from booking.domain.users.models import User

router = APIRouter(prefix="/v1/user", tags=["User"])


@router.get("/me", response_model=UserResponse, status_code=200)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user
