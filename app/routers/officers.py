from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.officer import Officer, OfficerCreate, OfficerRead, OfficerUpdate

router = APIRouter(
    prefix="/officers",
    tags=["Officers"]
)

@router.get("/", response_model=List[OfficerRead])
async def read_officers(*, session: Session = Depends(get_session), year: int = Query(default=None, ge=2000), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # TODO: Process query parameters to further limit results returned from database
    if year:
        officer_ids = session.exec(select(Officer.id).where(Officer.year == year).offset(offset).limit(limit)).all()
    else:
        officer_ids = session.exec(select(Officer.id).offset(offset).limit(limit)).all()
    return session.exec(select(Officer).where(Officer.id.in_(officer_ids))).all()

@router.post("/", response_model=OfficerRead)
async def create_officer(*, session: Session = Depends(get_session), officer: OfficerCreate):
    officer_db = Officer.from_orm(officer)
    session.add(officer_db)
    session.commit()
    session.refresh(officer_db)
    return officer_db

@router.get("/{officer_id}", response_model=OfficerRead)
async def read_officer(*, session: Session = Depends(get_session), officer_id: int):
    officer_db = session.get(Officer, officer_id)
    if not officer_db:
        raise HTTPException(status_code=404, detail="Officer not found")
    return officer_db

@router.patch("/{officer_id}", response_model=OfficerRead)
async def update_golfer(*, session: Session = Depends(get_session), officer_id: int, officer: OfficerUpdate):
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
async def delete_golfer(*, session: Session = Depends(get_session), officer_id: int):
    officer_db = session.get(Officer, officer_id)
    if not officer_db:
        raise HTTPException(status_code=404, detail="Officer not found")
    session.delete(officer_db)
    session.commit()
    return {"ok": True}
