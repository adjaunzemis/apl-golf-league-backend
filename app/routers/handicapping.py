from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlmodel import SQLModel, Session

from ..dependencies import get_session
from ..models.round import RoundData, RoundType
from ..models.tee import TeeGender
from ..models.query_helpers import get_rounds_in_scoring_record

from ..utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

router = APIRouter(
    prefix="/handicapping",
    tags=["Handicapping"]
)

# TODO: Change to or merge with RoundSummary?
class ScoringRecordEntry(SQLModel):
    date_played: date
    round_type: RoundType
    golfer_name: str
    course_name: str
    tee_name: str
    tee_gender: TeeGender
    tee_rating: float
    tee_slope: float
    adjusted_gross_score: int
    score_differential: float

class HandicapIndexWithScoringRecord(SQLModel):
    handicap_index: float
    date: date
    scoring_record: List[ScoringRecordEntry] = []

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
    return [ScoringRecordEntry(
        date_played=r.date_played,
        round_type=r.round_type,
        golfer_name=r.golfer_name,
        course_name=r.course_name,
        tee_name=r.tee_name,
        tee_gender=r.tee_gender,
        tee_rating=r.tee_rating,
        tee_slope=r.tee_slope,
        gross_score=r.gross_score,
        adjusted_gross_score=r.adjusted_gross_score,
        score_differential=r.score_differential) for r in rounds]

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
