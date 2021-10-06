from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.golfer import Golfer, GolferCreate, GolferUpdate, GolferRead

router = APIRouter(
    prefix="/golfers",
    tags=["Golfers"]
)

@router.get("/", response_model=List[GolferRead])
async def read_golfers(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Golfer).offset(offset).limit(limit)).all()

@router.post("/", response_model=GolferRead)
async def create_golfer(*, session: Session = Depends(get_session), golfer: GolferCreate):
    golfer_db = Golfer.from_orm(golfer)
    session.add(golfer_db)
    session.commit()
    session.refresh(golfer_db)
    return golfer_db

@router.get("/{golfer_id}", response_model=GolferRead)
async def read_golfer(*, session: Session = Depends(get_session), golfer_id: int):
    golfer_db = session.get(Golfer, golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=404, detail="Golfer not found")
    return golfer_db

@router.patch("/{golfer_id}", response_model=GolferRead)
async def update_golfer(*, session: Session = Depends(get_session), golfer_id: int, golfer: GolferUpdate):
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
async def delete_golfer(*, session: Session = Depends(get_session), golfer_id: int):
    golfer_db = session.get(Golfer, golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=404, detail="Golfer not found")
    session.delete(golfer_db)
    session.commit()
    return {"ok": True}
