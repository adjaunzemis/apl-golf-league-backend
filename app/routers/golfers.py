import re
from datetime import date, timedelta
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from app.database import golfers as db_golfers
from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.golfer import (
    Golfer,
    GolferCreate,
    GolferRead,
    GolferStatistics,
    GolferUpdate,
)
from app.models.query_helpers import (
    GolferData,
    GolferDataWithCount,
    GolferTeamData,
    get_golfer_team_data,
    get_golfers,
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
    golfer_ids = session.exec(select(Golfer.id).offset(offset).limit(limit)).all()
    # Return count of relevant golfers from database and golfer data list
    return GolferDataWithCount(
        num_golfers=len(golfer_ids),
        golfers=get_golfers(session=session, golfer_ids=golfer_ids),
    )


@router.get("/info", response_model=List[GolferRead])
async def read_all_golfers(*, session: Session = Depends(get_sql_db_session)):
    return session.exec(select(Golfer)).all()


@router.post("/", response_model=GolferRead)
async def create_golfer(
    *, session: Session = Depends(get_sql_db_session), golfer: GolferCreate
):
    # Validate entries
    if len(golfer.name) < 3:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid golfer name, too short (min: 3 characters)",
        )

    if len(golfer.name) > 25:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid golfer name, too long (max: 25 characters)",
        )

    if not bool(re.fullmatch(r"[a-zA-Z0-9\s\-\']+", golfer.name)):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid characters in golfer name",
        )

    if golfer.affiliation is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid golfer registration, affiliation is required",
        )

    if golfer.email is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid golfer registration, email is required",
        )

    # Convert name to title case
    golfer.name = golfer.name.title()

    # Add to database
    golfer_db = Golfer.model_validate(golfer)
    session.add(golfer_db)
    session.commit()
    session.refresh(golfer_db)
    return golfer_db


@router.get("/{golfer_id}", response_model=GolferData)
async def read_golfer(
    *,
    session: Session = Depends(get_sql_db_session),
    golfer_id: int,
    min_date: date = Query(default=date(date.today().year - 2, 1, 1)),
    max_date: date = Query(default=date.today() + timedelta(days=1)),
):
    golfer_db = get_golfers(
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
    golfer_db = session.get(Golfer, golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=404, detail="Golfer not found")
    golfer_data = golfer.model_dump(exclude_unset=True)
    for key, value in golfer_data.items():
        setattr(golfer_db, key, value)
    session.add(golfer_db)
    session.commit()
    session.refresh(golfer_db)
    return golfer_db


@router.delete("/{golfer_id}")
async def delete_golfer(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    golfer_id: int,
):
    golfer_db = session.get(Golfer, golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=404, detail="Golfer not found")
    session.delete(golfer_db)
    session.commit()
    return {"ok": True}


@router.get("/{golfer_id}/teams", response_model=List[GolferTeamData])
async def read_golfer_team_data(
    *,
    session: Session = Depends(get_sql_db_session),
    golfer_id: int,
    year: int | None = Query(default=None),
):
    return get_golfer_team_data(session=session, golfer_ids=(golfer_id,), year=year)


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
