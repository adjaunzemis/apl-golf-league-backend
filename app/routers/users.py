import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ..dependencies import get_session
from ..models.user import User, UserRead

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

load_dotenv()
APLGL_ACCESS_TOKEN_SECRET_KEY = os.environ.get("APLGL_ACCESS_TOKEN_SECRET_KEY")
APLGL_ACCESS_TOKEN_ALGORITHM = os.environ.get("APLGL_ACCESS_TOKEN_ALGORITHM")
APLGL_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("APLGL_ACCESS_TOKEN_EXPIRE_MINUTES"))

class Token(BaseModel):
    access_token: str
    access_token_expires_in: int
    token_type: str

class UserToken(Token):
    id: int
    username: str
    email: Optional[str] = None
    name: Optional[str] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def get_user(*, session: Session = Depends(get_session), username: str) -> User:
    return session.exec(select(User).where(User.username == username)).one_or_none()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(*, session: Session = Depends(get_session), username: str, password: str):
    user = get_user(session=session, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, APLGL_ACCESS_TOKEN_SECRET_KEY, algorithm=APLGL_ACCESS_TOKEN_ALGORITHM)
    return encoded_jwt

async def get_current_user(*, session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, APLGL_ACCESS_TOKEN_SECRET_KEY, algorithms=[APLGL_ACCESS_TOKEN_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(session=session, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@router.post("/token", response_model=UserToken)
async def login_for_access_token(*, session: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(session=session, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=APLGL_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return UserToken(
        id=user.id,
        username=user.username,
        email=user.email,
        name=user.name,
        access_token=access_token,
        access_token_expires_in=APLGL_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        token_type="bearer"
    )

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
