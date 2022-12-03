from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from ..dependencies import ACCESS_TOKEN_EXPIRE_MINUTES, get_session, authenticate_user, create_access_token, get_current_active_user
from ..models.user import User, UserRead, UserWithToken

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/token", response_model=UserWithToken)
async def login(*, session: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(session=session, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
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
        access_token_expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        token_type="bearer"
    )

@router.get("/me", response_model=UserRead)
async def get_current_user(*, current_user: User = Depends(get_current_active_user)):
    return current_user
