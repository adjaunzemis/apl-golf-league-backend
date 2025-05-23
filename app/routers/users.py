from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.dependencies import (
    authenticate_user,
    change_user_password,
    create_access_token,
    get_current_active_user,
    get_settings,
    get_sql_db_session,
)
from app.models.user import User, UserRead, UserWithToken

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/token", response_model=UserWithToken)
async def login(
    *,
    session: Session = Depends(get_sql_db_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(
        session=session, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return UserWithToken(
        id=user.id,
        username=user.username,
        email=user.email,
        name=user.name,
        disabled=user.disabled,
        is_admin=user.is_admin,
        edit_flights=user.edit_flights,
        edit_tournaments=user.edit_tournaments,
        edit_payments=user.edit_payments,
        access_token=access_token,
        access_token_expires_in=get_settings().apl_golf_league_api_access_token_expire_minutes
        * 60,
        token_type="bearer",
    )


@router.get("/me", response_model=UserRead)
async def get_current_user(*, current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/change-password", response_model=UserRead)
async def change_password(
    *,
    session: Session = Depends(get_sql_db_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    user = authenticate_user(
        session=session, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or old password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if (not current_user.is_admin) and (user.username != current_user.username):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized password change",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = change_user_password(
        session=session, username=form_data.username, password=form_data.client_secret
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
