from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query, HTTPException
from http import HTTPStatus
from sqlmodel import Session, select
from datetime import datetime
from app.utilities.apl_handicap_system import APLHandicapSystem

from app.utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

from ..dependencies import get_current_active_user, get_sql_db_session
from ..models.query_helpers import RoundSummary, HandicapIndexData, get_handicap_index_data, get_rounds_in_scoring_record
from ..models.qualifying_score import QualifyingScore, QualifyingScoreCreate, QualifyingScoreRead
from ..models.golfer import Golfer
from ..models.user import User

router = APIRouter(
    prefix="/handicaps",
    tags=["Handicaps"]
)

class QualifyingScoreInfo(QualifyingScoreRead):
    golfer_name: str

@router.get("/scoring-record/id={golfer_id}", response_model=List[RoundSummary])
async def get_scoring_record(*, session: Session = Depends(get_sql_db_session), golfer_id: int, min_date: date = Query(default=date(date.today().year - 2, 1, 1)), max_date: date = Query(default=date.today() + timedelta(days=1)), limit: int = Query(default=10), use_legacy_handicapping: bool = Query(default=False)):
    return get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, min_date=min_date, max_date=max_date, limit=limit, use_legacy_handicapping=use_legacy_handicapping)

@router.get("/handicap-index/id={golfer_id}", response_model=HandicapIndexData)
async def get_handicap_index(*, session: Session = Depends(get_sql_db_session), golfer_id: int = Query(default=None), min_date: date = Query(default=date(date.today().year - 2, 1, 1)), max_date: date = Query(default=date.today() + timedelta(days=1)), limit: int = Query(default=10), include_rounds: bool = Query(default=False), use_legacy_handicapping: bool = Query(default=False)):
    return get_handicap_index_data(session=session, golfer_id=golfer_id, min_date=min_date, max_date=max_date, limit=limit, include_rounds=include_rounds, use_legacy_handicapping=use_legacy_handicapping)

@router.get("/", response_model=List[QualifyingScoreInfo])
async def read_qualifying_scores(*, session: Session = Depends(get_sql_db_session), year: int):
    qualifying_score_data = session.exec(select(QualifyingScore, Golfer).join(Golfer, onclause=Golfer.id == QualifyingScore.golfer_id).where(QualifyingScore.year == year)).all()
    return [QualifyingScoreInfo(
        golfer_id=qualifying_score_db.golfer_id,
        golfer_name=golfer_db.name,
        year=qualifying_score_db.year,
        type=qualifying_score_db.type,
        score_differential=qualifying_score_db.score_differential,
        date_updated=qualifying_score_db.date_updated,
        date_played=qualifying_score_db.date_played,
        course_name=qualifying_score_db.course_name,
        track_name=qualifying_score_db.track_name,
        tee_name=qualifying_score_db.tee_name,
        tee_gender=qualifying_score_db.tee_gender,
        tee_par=qualifying_score_db.tee_par,
        tee_rating=qualifying_score_db.tee_rating,
        tee_slope=qualifying_score_db.tee_slope,
        gross_score=qualifying_score_db.gross_score,
        adjusted_gross_score=qualifying_score_db.adjusted_gross_score
    ) for qualifying_score_db, golfer_db in qualifying_score_data]

@router.post("/qualifying-score/", response_model=QualifyingScoreRead)
async def create_qualifying_score(*, session: Session = Depends(get_sql_db_session), current_user: User = Depends(get_current_active_user), qualifying_score: QualifyingScoreCreate, use_legacy_handicapping: bool = False):
    # TODO: Validate current user credentials
    # Validate and submit qualifying score data
    golfer_db = session.exec(select(Golfer).where(Golfer.id == qualifying_score.golfer_id)).one_or_none()
    if not golfer_db:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Qualifying score data invalid, no such golfer")
    qualifying_score_db = QualifyingScore.from_orm(qualifying_score)
    session.add(qualifying_score_db)
    session.commit()
    session.refresh(qualifying_score_db)
    # Update golfer handicap index (if possible)
    qualifying_scores_db = session.exec(select(QualifyingScore).where(QualifyingScore.golfer_id == golfer_db.id)).all()
    if len(qualifying_scores_db) > 1:
        if use_legacy_handicapping:
            handicap_system = APLLegacyHandicapSystem()
        else:
            handicap_system = APLHandicapSystem()
        golfer_db.handicap_index = handicap_system.compute_handicap_index(record=[qualifying_score.score_differential for qualifying_score in qualifying_scores_db])
        golfer_db.handicap_index_updated = datetime.now()
        session.add(golfer_db)
        session.commit()
        session.refresh(golfer_db)
    # Return new qualifying score database entry
    return qualifying_score_db

@router.get("/qualifying-score/{qualifying_score_id}", response_model=QualifyingScoreRead)
async def read_qualifying_score(*, session: Session = Depends(get_sql_db_session), qualifying_score_id: int):
    qualifying_score_db = session.get(QualifyingScore, qualifying_score_id)
    if not qualifying_score_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Qualifying score not found")
    return qualifying_score_db

@router.delete("/qualifying-score/{qualifying_score_id}")
async def delete_qualifying_score(*, session: Session = Depends(get_sql_db_session), current_user: User = Depends(get_current_active_user), qualifying_score_id: int):
    # TODO: Validate current user credentials
    qualifying_score_db = session.get(QualifyingScore, qualifying_score_id)
    if not qualifying_score_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Qualifying score not found")
    session.delete(qualifying_score_db)
    session.commit()
    return {"ok": True}
