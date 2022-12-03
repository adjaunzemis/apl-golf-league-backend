import os
from typing import Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Session, create_engine, select
from jose import JWTError, jwt
from passlib.context import CryptContext

from .models.user import User

load_dotenv()

""" Database """
DATABASE_CONNECTOR = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_CONNECTOR")
DATABASE_USER = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_PASSWORD")
DATABASE_URL = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_URL")
DATABASE_PORT = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_PORT_INTERNAL")
DATABASE_NAME = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_NAME")
DATABASE_ECHO = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_ECHO").lower() == 'true'

DATABASE_URL = f"{DATABASE_CONNECTOR}://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_URL}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL, echo=DATABASE_ECHO)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

""" Authentication """
ACCESS_TOKEN_SECRET_KEY = os.environ.get("APL_GOLF_LEAGUE_API_ACCESS_TOKEN_SECRET_KEY")
ACCESS_TOKEN_ALGORITHM = os.environ.get("APL_GOLF_LEAGUE_API_ACCESS_TOKEN_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("APL_GOLF_LEAGUE_API_ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def get_user(*, session: Session = Depends(get_session), username: str) -> User:
    return session.exec(select(User).where(User.username == username)).one_or_none()

def authenticate_user(*, session: Session = Depends(get_session), username: str, password: str):
    user = get_user(session=session, username=username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_TOKEN_SECRET_KEY, algorithm=ACCESS_TOKEN_ALGORITHM)
    return encoded_jwt

async def get_current_user(*, session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ACCESS_TOKEN_SECRET_KEY, algorithms=[ACCESS_TOKEN_ALGORITHM])
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