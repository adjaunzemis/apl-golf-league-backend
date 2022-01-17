from typing import List
from datetime import date, timezone, datetime
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

class HandicapIndexWithScoringRecord(SQLModel):
    handicap_index: float
    date: date
    scoring_record: List[ScoringRecordEntry] = []

# TODO: Add score differential to round data on creation or import to database
def create_scoring_record_from_rounds(rounds: List[RoundData]) -> List[ScoringRecordEntry]:
    """
    Extracts scoring record data from round data.

    Parameters
    ----------
    rounds : list of RoundData
        round data

    Returns
    -------
    record : list of ScoringRecordEntry
        scoring record

    """
    ahs = APLLegacyHandicapSystem()
    return [ScoringRecordEntry(
        date=r.date_played,
        score_differential=ahs.compute_score_differential(r.tee_rating, r.tee_slope, r.adjusted_gross_score),
        rating=r.tee_rating,
        slope=r.tee_slope,
        gross_score=r.gross_score,
        adjusted_gross_score=r.adjusted_gross_score) for r in rounds]

@router.get("/scoring-record/id={golfer_id}", response_model=List[ScoringRecordEntry])
async def get_scoring_record(*, session: Session = Depends(get_session), golfer_id: int, date: date = Query(default=date.today())):
    rounds = get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, date=date, limit=10)
    return create_scoring_record_from_rounds(rounds=rounds)

@router.get("/handicap-index/id={golfer_id}", response_model=HandicapIndexWithScoringRecord)
async def get_handicap_index(*, session: Session = Depends(get_session), golfer_id: int = Query(default=None), date: date = Query(default=date.today()), include_record: bool = Query(default=False)):
    ahs = APLLegacyHandicapSystem()
    rounds = get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, date=date, limit=10)
    record = [ahs.compute_score_differential(r.tee_rating, r.tee_slope, r.adjusted_gross_score) for r in rounds]
    response = HandicapIndexWithScoringRecord(date=date, handicap_index=ahs.compute_handicap_index(record=record))
    if include_record:
        response.scoring_record = create_scoring_record_from_rounds(rounds=rounds)
    return response
