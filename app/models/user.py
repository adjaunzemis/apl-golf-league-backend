from typing import Optional
from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    username: str
    email: Optional[str] = None
    name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None
    edit_flights: Optional[bool] = False
    edit_tournaments: Optional[bool] = False
    edit_payments: Optional[bool] = False

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = None

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    username: Optional[str] = None
    hashed_password: Optional[str] = None
    email: Optional[int] = None
    name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None
    edit_flights: Optional[bool] = None
    edit_tournaments: Optional[bool] = None
    edit_payments: Optional[bool] = None

class UserRead(UserBase):
    id: int

class UserWithToken(UserRead):
    id: int
    access_token: str
    access_token_expires_in: int
    token_type: str
