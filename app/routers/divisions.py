from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.division import Division, DivisionCreate, DivisionUpdate, DivisionRead

router = APIRouter(
    prefix="/divisions",
    tags=["Divisions"]
)

@router.get("/", response_model=List[DivisionRead])
async def read_divisions(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Division).offset(offset).limit(limit)).all()

@router.post("/", response_model=DivisionRead)
async def create_division(*, session: Session = Depends(get_session), division: DivisionCreate):
    division_db = Division.from_orm(division)
    session.add(division_db)
    session.commit()
    session.refresh(division_db)
    return division_db

@router.get("/{division_id}", response_model=DivisionRead)
async def read_division(*, session: Session = Depends(get_session), division_id: int):
    division_db = session.get(Division, division_id)
    if not division_db:
        raise HTTPException(status_code=404, detail="Division not found")
    return division_db

@router.patch("/{division_id}", response_model=DivisionRead)
async def update_division(*, session: Session = Depends(get_session), division_id: int, division: DivisionUpdate):
    division_db = session.get(Division, division_id)
    if not division_db:
        raise HTTPException(status_code=404, detail="Division not found")
    division_data = division.dict(exclude_unset=True)
    for key, value in division_data.items():
        setattr(division_db, key, value)
    session.add(division_db)
    session.commit()
    session.refresh(division_db)
    return division_db

@router.delete("/{division_id}")
async def delete_division(*, session: Session = Depends(get_session), division_id: int):
    division_db = session.get(Division, division_id)
    if not division_db:
        raise HTTPException(status_code=404, detail="Division not found")
    session.delete(division_db)
    session.commit()
    return {"ok": True}
