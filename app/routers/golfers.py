from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.golfer import Golfer, GolferCreate, GolferRead, GolferUpdate
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
    golfer_db = Golfer.from_orm(golfer)
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
    golfer_data = golfer.dict(exclude_unset=True)
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
    year: int = Query(default=None),
):
    return get_golfer_team_data(session=session, golfer_ids=(golfer_id,), year=year)
