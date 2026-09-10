import re
from datetime import date, timedelta
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session

from app.database import golfers as db_golfers
from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.golfer import (
    GolferCreate,
    GolferRead,
    GolferStatistics,
    GolferUpdate,
)
from app.models.query_helpers import (
    GolferData,
    GolferDataWithCount,
    GolferTeamData,
)
from app.models.user import User

router = APIRouter(prefix="/golfers", tags=["Golfers"])


@router.get("/", response_model=GolferDataWithCount)
async def read_golfers(
    *,
    session: Session = Depends(get_sql_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100),
):
    # TODO: Process query parameters to further limit golfer results returned from database
    golfer_ids = db_golfers.get_ids(session=session, offset=offset, limit=limit)
    # Return count of relevant golfers from database and golfer data list
    return GolferDataWithCount(
        num_golfers=len(golfer_ids),
        golfers=db_golfers.get_golfers(session=session, golfer_ids=golfer_ids),
    )


@router.get("/info", response_model=List[GolferRead])
async def read_all_golfers(*, session: Session = Depends(get_sql_db_session)):
    return db_golfers.get_all(session=session)


def validate_golfer_name(
    session: Session, name: str, exclude_golfer_id: int | None = None
) -> str:
    if len(name) < 3:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid golfer name, too short (min: 3 characters)",
        )

    if len(name) > 25:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid golfer name, too long (max: 25 characters)",
        )

    if not bool(re.fullmatch(r"[a-zA-Z0-9\s\-\']+", name)):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid characters in golfer name",
        )

    formatted_name = name.title()
    name_check = db_golfers.check_golfer_name_uniqueness(
        session=session,
        name=formatted_name,
        hard_block_threshold=0.9,
        exclude_golfer_id=exclude_golfer_id,
    )
    if not name_check.is_unique:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Invalid golfer registration, golfer with name '{formatted_name}' already exists",
        )

    return formatted_name


@router.post("/", response_model=GolferRead)
async def create_golfer(
    *, session: Session = Depends(get_sql_db_session), golfer: GolferCreate
):
    # Validate entries
    golfer.name = validate_golfer_name(session=session, name=golfer.name)

    if golfer.affiliation is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid golfer registration, affiliation is required",
        )

    if golfer.email is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid golfer registration, email is required",
        )

    # Add to database
    return db_golfers.create_golfer(session=session, golfer=golfer)


@router.get("/{golfer_id}", response_model=GolferData)
async def read_golfer(
    *,
    session: Session = Depends(get_sql_db_session),
    golfer_id: int,
    min_date: date = Query(default=date(date.today().year - 2, 1, 1)),
    max_date: date = Query(default=date.today() + timedelta(days=1)),
):
    golfer_db = db_golfers.get_golfers(
        session=session,
        golfer_ids=[
            golfer_id,
        ],
        min_date=min_date,
        max_date=max_date,
        include_scoring_record=True,
        use_legacy_handicapping=False,
    )
    if (not golfer_db) or (len(golfer_db) == 0):
        raise HTTPException(status_code=404, detail="Golfer not found")
    return golfer_db[0]


@router.patch("/{golfer_id}", response_model=GolferRead)
async def update_golfer(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    golfer_id: int,
    golfer: GolferUpdate,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to update golfers",
        )

    golfer_db = db_golfers.get_by_id(session, golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Golfer not found")

    if golfer.name is not None:
        golfer.name = validate_golfer_name(
            session=session, name=golfer.name, exclude_golfer_id=golfer_id
        )

    return db_golfers.update_golfer(
        session=session, golfer_id=golfer_id, golfer_update=golfer
    )


@router.delete("/{golfer_id}")
async def delete_golfer(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    golfer_id: int,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to delete golfers",
        )

    golfer_db = db_golfers.delete_golfer(session=session, golfer_id=golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Golfer not found")
    return {"ok": True}


@router.get("/{golfer_id}/teams", response_model=List[GolferTeamData])
async def read_golfer_team_data(
    *,
    session: Session = Depends(get_sql_db_session),
    golfer_id: int,
    year: int | None = Query(default=None),
):
    return db_golfers.get_golfer_team_data(
        session=session, golfer_ids=(golfer_id,), year=year
    )


@router.get("/{golfer_id}/statistics", response_model=GolferStatistics)
async def get_statistics(
    *,
    session: Session = Depends(get_sql_db_session),
    golfer_id: int,
    year: int | None = Query(default=None),
):
    stats = db_golfers.get_statistics(session=session, golfer_id=golfer_id, year=year)
    if stats is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Golfer not found")
    return stats
