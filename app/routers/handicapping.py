from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import SQLModel, Session, select

from ..dependencies import get_session
from ..models.round import RoundData
from ..models.query_helpers import get_rounds_in_scoring_record

from ..utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

router = APIRouter(
    prefix="/handicapping",
    tags=["Handicapping"]
)

class ScoringRecordEntry(SQLModel):
    date: date
    score_differential: float
    rating: float
    slope: float
    gross_score: int
    adjusted_gross_score: int

# TODO: Add score differential to round data on creation or import to database
@router.get("/scoring-record/id={golfer_id}&date={date}", response_model=List[ScoringRecordEntry])
async def get_scoring_record(*, session: Session = Depends(get_session), golfer_id: int, date: date):
    rounds = get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, date=date, limit=10)
    ahs = APLLegacyHandicapSystem()
    return [ScoringRecordEntry(
        date=r.date_played,
        score_differential=ahs.compute_score_differential(r.tee_rating, r.tee_slope, r.adjusted_gross_score),
        rating=r.tee_rating,
        slope=r.tee_slope,
        gross_score=r.gross_score,
        adjusted_gross_score=r.adjusted_gross_score) for r in rounds]
