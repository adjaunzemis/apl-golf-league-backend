from functools import lru_cache
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.future import Engine
from jose import JWTError, jwt
from passlib.context import CryptContext

from .models.user import User
from .config import Settings

@lru_cache()
def get_settings():
    return Settings()

""" SQL Database """
@lru_cache()
def get_sql_db_engine() -> Engine:
    settings = get_settings()
    db_uri = f"{settings.apl_golf_league_api_database_connector}://{settings.apl_golf_league_api_database_user}:{settings.apl_golf_league_api_database_password}@{settings.apl_golf_league_api_database_url}:{settings.apl_golf_league_api_database_port_internal}/{settings.apl_golf_league_api_database_name}"
    return create_engine(db_uri, echo=settings.apl_golf_league_api_database_echo)

def create_sql_db_and_tables() -> None:
    SQLModel.metadata.create_all(get_sql_db_engine())

def get_session() -> Session:
    with Session(get_sql_db_engine()) as session:
        yield session

""" Authentication """
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

def create_access_token(*, settings: Settings = Depends(get_settings), data: dict):
    to_encode = data.copy()
    expire_time = datetime.utcnow() + timedelta(minutes=settings.apl_golf_league_api_access_token_expire_minutes)
    to_encode.update({"exp": expire_time})
    encoded_jwt = jwt.encode(to_encode, settings.apl_golf_league_api_access_token_secret_key, algorithm=settings.apl_golf_league_api_access_token_algorithm)
    return encoded_jwt

async def get_current_user(*, settings: Settings = Depends(get_settings), session: Session = Depends(get_session), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.apl_golf_league_api_access_token_secret_key, algorithms=[settings.apl_golf_league_api_access_token_algorithm])
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
