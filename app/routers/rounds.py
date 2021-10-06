from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.round import Round, RoundCreate, RoundUpdate, RoundRead, RoundReadWithTeeAndGolfer

router = APIRouter(
    prefix="/rounds",
    tags=["Rounds"]
)

@router.get("/", response_model=List[RoundRead])
async def read_rounds(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Round).offset(offset).limit(limit)).all()

@router.post("/", response_model=RoundRead)
async def create_round(*, session: Session = Depends(get_session), round: RoundCreate):
    round_db = Round.from_orm(round)
    session.add(round_db)
    session.commit()
    session.refresh(round_db)
    return round_db

@router.get("/{round_id}", response_model=RoundReadWithTeeAndGolfer)
async def read_round(*, session: Session = Depends(get_session), round_id: int):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    return round_db

@router.patch("/{round_id}", response_model=RoundRead)
async def update_round(*, session: Session = Depends(get_session), round_id: int, round: RoundUpdate):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    round_data = round.dict(exclude_unset=True)
    for key, value in round_data.items():
        setattr(round_db, key, value)
    session.add(round_db)
    session.commit()
    session.refresh(round_db)
    return round_db

@router.delete("/{round_id}")
async def delete_round(*, session: Session = Depends(get_session), round_id: int):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    session.delete(round_db)
    session.commit()
    return {"ok": True}
