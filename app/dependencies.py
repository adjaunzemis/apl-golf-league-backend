from datetime import datetime, timedelta
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import MongoClient
from sqlalchemy.future import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from app.config import Settings
from app.models.user import User


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


def get_sql_db_session() -> Session:
    with Session(get_sql_db_engine()) as session:
        yield session


""" NoSQL Database """


@lru_cache()
def get_nosql_db_client() -> MongoClient:
    settings = get_settings()
    CONNECTOR = "mongodb"
    USERNAME = "TestAppUser"
    PASSWORD = "TestAppPassword"
    URL = "mongodb"
    PORT = 27017
    AUTH_SOURCE = "TestDB"
    db_uri = f"{CONNECTOR}://{USERNAME}:{PASSWORD}@{URL}:{PORT}/?serverSelectionTimeoutMS=5000&connectTimeoutMS=10000&authSource={AUTH_SOURCE}&authMechanism=SCRAM-SHA-256"
    return MongoClient(db_uri)


def create_nosql_db_and_collections() -> None:
    get_nosql_db_client()


def close_nosql_db() -> None:
    get_nosql_db_client().close()


""" Authentication """
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def get_user(*, session: Session = Depends(get_sql_db_session), username: str) -> User:
    return session.exec(select(User).where(User.username == username)).one_or_none()


def authenticate_user(
    *, session: Session = Depends(get_sql_db_session), username: str, password: str
):
    user = get_user(session=session, username=username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def change_user_password(
    *, session: Session = Depends(get_sql_db_session), username: str, password: str
):
    user = get_user(session=session, username=username)
    if not user:
        return False

    # TODO: check validity of new password

    setattr(user, "hashed_password", pwd_context.hash(password))
    session.commit()
    session.refresh(user)
    return user


def create_access_token(*, data: dict):
    to_encode = data.copy()
    expire_time = datetime.utcnow() + timedelta(
        minutes=get_settings().apl_golf_league_api_access_token_expire_minutes
    )
    to_encode.update({"exp": expire_time})
    encoded_jwt = jwt.encode(
        to_encode,
        get_settings().apl_golf_league_api_access_token_secret_key,
        algorithm=get_settings().apl_golf_league_api_access_token_algorithm,
    )
    return encoded_jwt


async def get_current_user(
    *,
    session: Session = Depends(get_sql_db_session),
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            get_settings().apl_golf_league_api_access_token_secret_key,
            algorithms=[get_settings().apl_golf_league_api_access_token_algorithm],
        )
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
