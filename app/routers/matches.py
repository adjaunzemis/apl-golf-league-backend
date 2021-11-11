from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.flight import Flight, FlightCreate, FlightUpdate, FlightRead, FlightReadWithData, FlightData, FlightDataWithCount
from ..models.division import Division, DivisionCreate, DivisionUpdate, DivisionRead, DivisionData
from ..models.team import Team, TeamCreate, TeamUpdate, TeamRead, TeamReadWithPlayers, TeamData
from ..models.player import Player, PlayerCreate, PlayerUpdate, PlayerRead, PlayerReadWithData, PlayerData
from ..models.match import Match, MatchCreate, MatchUpdate, MatchRead, MatchReadWithData
from ..models.match_round_link import MatchRoundLink
from ..models.course import Course
from ..models.tee import Tee
from ..models.golfer import Golfer

router = APIRouter(
    prefix="/matches",
    tags=["Matches"]
)

@router.get("/", response_model=List[MatchRead])
async def read_matches(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Match).offset(offset).limit(limit)).all()

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
