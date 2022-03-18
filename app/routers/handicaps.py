from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..dependencies import get_session
from ..models.query_helpers import RoundSummary, HandicapIndexData, get_handicap_index_data, get_rounds_in_scoring_record

router = APIRouter(
    prefix="/handicaps",
    tags=["Handicaps"]
)

@router.get("/scoring-record/id={golfer_id}", response_model=List[RoundSummary])
async def get_scoring_record(*, session: Session = Depends(get_session), golfer_id: int, max_date: date = Query(default=date.today()), limit: int = Query(default=10)):
    return get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, max_date=max_date, limit=limit)

@router.get("/handicap-index/id={golfer_id}", response_model=HandicapIndexData)
async def get_handicap_index(*, session: Session = Depends(get_session), golfer_id: int = Query(default=None), min_date: date = Query(default=date(date.today().year - 2, 1, 1)), max_date: date = Query(default=date.today()), limit: int = Query(default=10), include_rounds: bool = Query(default=False)):
    return get_handicap_index_data(session=session, golfer_id=golfer_id, min_date=min_date, max_date=max_date, limit=limit, include_rounds=include_rounds, use_legacy_handicapping=True)
