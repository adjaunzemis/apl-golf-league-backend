from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from http import HTTPStatus
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_session
from ..models.query_helpers import RoundSummary, HandicapIndexData, get_handicap_index_data, get_rounds_in_scoring_record
from ..models.qualifying_score import QualifyingScore, QualifyingScoreCreate, QualifyingScoreRead, QualifyingScoreUpdate
from ..models.golfer import Golfer
from ..models.user import User

router = APIRouter(
    prefix="/handicaps",
    tags=["Handicaps"]
)

class QualifyingScoreInfo(QualifyingScoreRead):
    golfer_name: str

@router.get("/scoring-record/id={golfer_id}", response_model=List[RoundSummary])
async def get_scoring_record(*, session: Session = Depends(get_session), golfer_id: int, max_date: date = Query(default=date.today()), limit: int = Query(default=10)):
    return get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, max_date=max_date, limit=limit)

@router.get("/handicap-index/id={golfer_id}", response_model=HandicapIndexData)
async def get_handicap_index(*, session: Session = Depends(get_session), golfer_id: int = Query(default=None), min_date: date = Query(default=date(date.today().year - 2, 1, 1)), max_date: date = Query(default=date.today()), limit: int = Query(default=10), include_rounds: bool = Query(default=False)):
    return get_handicap_index_data(session=session, golfer_id=golfer_id, min_date=min_date, max_date=max_date, limit=limit, include_rounds=include_rounds, use_legacy_handicapping=True)

@router.get("/", response_model=List[QualifyingScoreInfo])
async def read_qualifying_scores(*, session: Session = Depends(get_session), year: int):
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

@router.put("/", response_model=QualifyingScoreRead)
async def create_qualifying_score(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), qualifying_score: QualifyingScoreCreate):
    # TODO: Validate current user credentials
    qualifying_score_db = QualifyingScore.from_orm(qualifying_score)
    session.add(qualifying_score_db)
    session.commit()
    session.refresh(qualifying_score_db)
    return qualifying_score_db

@router.get("/{qualifying_score_id}", response_model=QualifyingScoreRead)
async def read_qualifying_score(*, session: Session = Depends(get_session), qualifying_score_id: int):
    qualifying_score_db = session.get(QualifyingScore, qualifying_score_id)
    if not qualifying_score_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Qualifying score not found")
    return qualifying_score_db

@router.patch("/{qualifying_score_id}", response_model=QualifyingScoreRead)
async def update_qualifying_score(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), qualifying_score_id: int, qualifying_score: QualifyingScoreUpdate):
    # TODO: Validate current user credentials
    qualifying_score_db = session.get(QualifyingScore, qualifying_score_id)
    if not qualifying_score_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Qualifying score not found")
    qualifying_score_data = qualifying_score.dict(exclude_unset=True)
    for key, value in qualifying_score_data.items():
        setattr(qualifying_score_db, key, value)
    session.add(qualifying_score_db)
    session.commit()
    session.refresh(qualifying_score_db)
    return qualifying_score_db

@router.delete("/{qualifying_score_id}")
async def delete_qualifying_score(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), qualifying_score_id: int):
    # TODO: Validate current user credentials
    qualifying_score_db = session.get(QualifyingScore, qualifying_score_id)
    if not qualifying_score_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Qualifying score not found")
    session.delete(qualifying_score_db)
    session.commit()
    return {"ok": True}
