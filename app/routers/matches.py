from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select, SQLModel

from app.models.query_helpers import get_rounds_for_matches

from ..dependencies import get_session
from ..models.match import Match, MatchCreate, MatchUpdate, MatchRead, MatchReadWithData, MatchData, MatchDataWithCount
from ..models.match_round_link import MatchRoundLink
from ..models.round import Round, RoundData
from ..models.course import Course
from ..models.track import Track
from ..models.tee import Tee
from ..models.hole import Hole
from ..models.hole_result import HoleResult, HoleResultData
from ..models.golfer import Golfer
from ..models.player import Player
from ..models.flight import Flight
from ..models.team import Team
from ..utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

router = APIRouter(
    prefix="/matches",
    tags=["Matches"]
)

@router.get("/", response_model=MatchDataWithCount)
async def read_matches(*, session: Session = Depends(get_session), team_id: int = Query(default=None, ge=0), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # Process query parameters to further limit match results returned from database
    if team_id: # limit to specific team
        num_matches = len(session.exec(select(Match.id).where(Match.home_team_id == team_id or Match.away_team_id == team_id)).all())
        match_query_data = session.exec(select(Match, Flight).join(Flight).where(Match.home_team_id == team_id or Match.away_team_id == team_id).offset(offset).limit(limit).order_by(Match.week))
    else: # no extra limitations
        num_matches = len(session.exec(select(Match.id)).all())
        match_query_data = session.exec(select(Match, Flight).join(Flight).offset(offset).limit(limit).order_by(Match.week))

    # Reformat matches data
    if num_matches == 0:
        return MatchDataWithCount(num_matches=0, matches=[])

    match_data = [MatchData(
        match_id=match.id,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        flight_name=flight.name,
        week=match.week,
        home_score=match.home_score,
        away_score=match.away_score
    ) for match, flight in match_query_data]
    
    # Add round data to match data
    round_data = get_rounds_for_matches(session=session, match_ids=[m.match_id for m in match_data])
    for m in match_data:
        m.rounds = [r for r in round_data if r.match_id == m.match_id]

    # Return count of relevant matches from database and match data list
    return MatchDataWithCount(num_matches=num_matches, matches=match_data)

@router.post("/", response_model=MatchRead)
async def create_match(*, session: Session = Depends(get_session), match: MatchCreate):
    match_db = Match.from_orm(match)
    session.add(match_db)
    session.commit()
    session.refresh(match_db)
    return match_db

@router.get("/{match_id}", response_model=MatchReadWithData)
async def read_match(*, session: Session = Depends(get_session), match_id: int):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Match not found")
    return match_db

@router.patch("/{match_id}", response_model=MatchRead)
async def update_match(*, session: Session = Depends(get_session), match_id: int, match: MatchUpdate):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Match not found")
    match_data = match.dict(exclude_unset=True)
    for key, value in match_data.items():
        setattr(match_db, key, value)
    session.add(match_db)
    session.commit()
    session.refresh(match_db)
    return match_db

@router.delete("/{match_id}")
async def delete_match(*, session: Session = Depends(get_session), match_id: int):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Match not found")
    session.delete(match_db)
    session.commit()
    return {"ok": True}

@router.get("/rounds/", response_model=List[MatchRoundLink])
async def read_match_round_links(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(MatchRoundLink).offset(offset).limit(limit)).all()

@router.get("/{match_id}/rounds/", response_model=List[MatchRoundLink])
async def read_match_round_links_for_match(*, session: Session = Depends(get_session), match_id: int):
    return session.exec(select(MatchRoundLink).where(MatchRoundLink.match_id == match_id)).all()

@router.post("/{match_id}/rounds/{round_id}", response_model=MatchRoundLink)
async def create_match_round_link(*, session: Session = Depends(get_session), match_id: int, round_id: int):
    link_db = MatchRoundLink(match_id=match_id, round_id=round_id)
    session.add(link_db)
    session.commit()
    session.refresh(link_db)
    return link_db

@router.delete("/{match_id}/rounds/{round_id}")
async def delete_match_round_link(*, session: Session = Depends(get_session), match_id: int, round_id: int):
    link_db = session.get(MatchRoundLink, [match_id, round_id])
    if not link_db:
        raise HTTPException(status_code=404, detail="Match-Round link not found")
    session.delete(link_db)
    session.commit()
    return {"ok": True}
