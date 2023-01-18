from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_sql_db_session
from ..models.officer import Officer, OfficerCreate, OfficerRead, OfficerUpdate
from ..models.user import User

router = APIRouter(prefix="/officers", tags=["Officers"])


@router.get("/", response_model=List[OfficerRead])
async def read_officers(
    *,
    session: Session = Depends(get_sql_db_session),
    year: int = Query(default=None, ge=2000)
):
    if year:  # filter to a certain year
        officer_ids = session.exec(select(Officer.id).where(Officer.year == year)).all()
    else:  # get all
        officer_ids = session.exec(select(Officer.id)).all()
    return session.exec(select(Officer).where(Officer.id.in_(officer_ids))).all()


@router.post("/", response_model=OfficerRead)
async def create_officer(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    officer: OfficerCreate
):
    officer_db = Officer.from_orm(officer)
    session.add(officer_db)
    session.commit()
    session.refresh(officer_db)
    return officer_db


@router.get("/{officer_id}", response_model=OfficerRead)
async def read_officer(
    *, session: Session = Depends(get_sql_db_session), officer_id: int
):
    officer_db = session.get(Officer, officer_id)
    if not officer_db:
        raise HTTPException(status_code=404, detail="Officer not found")
    return officer_db


@router.patch("/{officer_id}", response_model=OfficerRead)
async def update_officer(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    officer_id: int,
    officer: OfficerUpdate
):
    officer_db = session.get(Officer, officer_id)
    if not officer_db:
        raise HTTPException(status_code=404, detail="Officer not found")
    officer_data = officer.dict(exclude_unset=True)
    for key, value in officer_data.items():
        setattr(officer_db, key, value)
    session.add(officer_db)
    session.commit()
    session.refresh(officer_db)
    return officer_db


@router.delete("/{officer_id}")
async def delete_officer(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    officer_id: int
):
    officer_db = session.get(Officer, officer_id)
    if not officer_db:
        raise HTTPException(status_code=404, detail="Officer not found")
    session.delete(officer_db)
    session.commit()
    return {"ok": True}
