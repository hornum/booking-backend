from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class AuthResponse(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
