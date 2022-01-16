from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.round import Round, RoundCreate, RoundData, RoundUpdate, RoundRead, RoundReadWithData, RoundDataWithCount
from ..models.hole_result import HoleResult, HoleResultCreate, HoleResultUpdate, HoleResultRead, HoleResultReadWithHole
from ..models.query_helpers import get_rounds, get_rounds_in_scoring_record

router = APIRouter(
    prefix="/rounds",
    tags=["Rounds"]
)
    
@router.get("/", response_model=RoundDataWithCount)
async def read_rounds(*, session: Session = Depends(get_session), golfer_id: int = Query(default=None, ge=0), offset: int = Query(default=0, ge=0), limit: int = Query(default=25, ge=0, le=100)):
    # Process query parameters to limit results
    if golfer_id: # limit to specific golfer
        round_ids = session.exec(select(Round.id).where(Round.golfer_id == golfer_id).offset(offset).limit(limit)).all()
    else: # no extra limitations
        round_ids = session.exec(select(Round.id).offset(offset).limit(limit)).all()

    # Return count of relevant rounds from database and round data list
    return RoundDataWithCount(num_rounds=len(round_ids), matches=get_rounds(session=session, round_ids=round_ids))

@router.post("/", response_model=RoundRead)
async def create_round(*, session: Session = Depends(get_session), round: RoundCreate):
    round_db = Round.from_orm(round)
    session.add(round_db)
    session.commit()
    session.refresh(round_db)
    return round_db

@router.get("/{round_id}", response_model=RoundReadWithData)
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

@router.get("/hole_results/", response_model=List[HoleResultRead])
async def read_hole_results(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(HoleResult).offset(offset).limit(limit)).all()

@router.post("/hole_results/", response_model=HoleResultRead)
async def create_hole_result(*, session: Session = Depends(get_session), hole_result: HoleResultCreate):
    hole_result_db = HoleResult.from_orm(hole_result)
    session.add(hole_result_db)
    session.commit()
    session.refresh(hole_result_db)
    return hole_result_db

@router.get("/hole_results/{hole_result_id}", response_model=HoleResultReadWithHole)
async def read_hole_result(*, session: Session = Depends(get_session), hole_result_id: int):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    return hole_result_db

@router.patch("/hole_results/{hole_result_id}", response_model=HoleResultRead)
async def update_hole_result(*, session: Session = Depends(get_session), hole_result_id: int, hole_result: HoleResultUpdate):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    round_data = hole_result.dict(exclude_unset=True)
    for key, value in round_data.items():
        setattr(hole_result_db, key, value)
    session.add(hole_result_db)
    session.commit()
    session.refresh(hole_result_db)
    return hole_result_db

@router.delete("/hole_results/{hole_result_id}")
async def delete_hole_result(*, session: Session = Depends(get_session), hole_result_id: int):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    session.delete(hole_result_db)
    session.commit()
    return {"ok": True}

# TODO: Move to handicapping router?
@router.get("/scoring-record/id={golfer_id}&date={date}", response_model=List[RoundData])
async def get_scoring_record(*, session: Session = Depends(get_session), golfer_id: int, date: date):
    return get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, date=date, limit=10)
