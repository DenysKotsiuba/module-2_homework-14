from pydantic import BaseModel, Field, EmailStr

from datetime import datetime


class UserModel(BaseModel):
    username: str = Field(max_length=50)
    email: EmailStr
    password: str = Field(max_length=255)


class UserDB(BaseModel):
    id: int
    username: str
    email: EmailStr
    create_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponseModel(BaseModel):
    user: UserDB
    detail: str


class TokenResponseModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr