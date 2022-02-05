from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import true
from sqlmodel import Session

from ..dependencies import get_session
from ..models.query_helpers import RoundSummary, HandicapIndexData, get_handicap_index_data, get_rounds_in_scoring_record

router = APIRouter(
    prefix="/handicapping",
    tags=["Handicapping"]
)

@router.get("/scoring-record/id={golfer_id}", response_model=List[RoundSummary])
async def get_scoring_record(*, session: Session = Depends(get_session), golfer_id: int, date: date = Query(default=date.today()), limit: int = Query(default=10)):
    return get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, date=date, limit=limit)

@router.get("/handicap-index/id={golfer_id}", response_model=HandicapIndexData)
async def get_handicap_index(*, session: Session = Depends(get_session), golfer_id: int = Query(default=None), date: date = Query(default=date.today()), limit: int = Query(default=10), include_record: bool = Query(default=False)):
    return get_handicap_index_data(session=session, golfer_id=golfer_id, date=date, limit=limit, include_record=include_record, use_legacy_handicapping=True)
