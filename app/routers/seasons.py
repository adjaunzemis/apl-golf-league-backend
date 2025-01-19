from typing import List

from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session

from app.database import seasons as db_seasons
from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.seasons import Season, SeasonCreate
from app.models.user import User

router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.get("/", response_model=List[Season])
async def get_seasons(
    *,
    session: Session = Depends(get_sql_db_session),
):
    return db_seasons.get_seasons(session)


@router.get("/{year}", response_model=Season)
async def get_season_by_year(
    *,
    session: Session = Depends(get_sql_db_session),
    year: int = Path(..., description="Season year"),
):
    season_db = db_seasons.get_season_by_year(session, year)
    if season_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Season not found"
        )
    return season_db


@router.post("/", response_model=Season)
async def create_season(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    new_season: SeasonCreate = Body(..., description="New season to add"),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient privileges to create season",
        )
    season_db = db_seasons.create_season(session, new_season)
    if season_db is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unable to create season",
        )
    return season_db


@router.get("/active/", response_model=Season)
async def get_active_season(*, session: Session = Depends(get_sql_db_session)):
    season_db = db_seasons.get_active_season(session)
    if season_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to find current active season",
        )
    return season_db


@router.patch("/active/{year}", response_model=Season)
async def set_active_season(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    year: int = Path(..., description="Year of season to set active"),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient privileges to set active season",
        )
    season_db = db_seasons.set_active_season(session, year)
    if season_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Season not found"
        )
    return season_db


@router.delete("/{year}")
async def delete_season(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    year: int,
) -> Season:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient privileges to delete season",
        )
    season_db = db_seasons.delete_season(session, year)
    if season_db is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to delete season",
        )
    return season_db
