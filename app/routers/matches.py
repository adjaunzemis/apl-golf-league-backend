from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select


from ..dependencies import get_current_active_user, get_session
from ..models.match import Match, MatchCreate, MatchUpdate, MatchRead, MatchData, MatchDataWithCount
from ..models.match_round_link import MatchRoundLink
from ..models.user import User
from ..models.query_helpers import get_matches

router = APIRouter(
    prefix="/matches",
    tags=["Matches"]
)

@router.get("/", response_model=MatchDataWithCount)
async def read_matches(*, session: Session = Depends(get_session), team_id: int = Query(default=None, ge=0), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # Process query parameters to limit results
    if team_id: # limit to specific team
        match_ids = session.exec(select(Match.id).where(Match.home_team_id == team_id or Match.away_team_id == team_id).offset(offset).limit(limit)).all()
    else: # no extra limitations
        match_ids = session.exec(select(Match.id).offset(offset).limit(limit)).all()

    # Return count of relevant matches from database and match data list
    return MatchDataWithCount(num_matches=len(match_ids), matches=get_matches(session=session, match_ids=match_ids))

@router.post("/", response_model=MatchRead)
async def create_match(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), match: MatchCreate):
    match_db = Match.from_orm(match)
    session.add(match_db)
    session.commit()
    session.refresh(match_db)
    return match_db

@router.get("/{match_id}", response_model=MatchData)
async def read_match(*, session: Session = Depends(get_session), match_id: int):
    match_db = get_matches(session=session, match_ids=(match_id,))
    if (not match_db) or (len(match_db) != 1):
        raise HTTPException(status_code=404, detail="Match not found")
    return match_db[0]

@router.patch("/{match_id}", response_model=MatchRead)
async def update_match(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), match_id: int, match: MatchUpdate):
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
async def delete_match(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), match_id: int):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Match not found")
    session.delete(match_db)
    session.commit()
    # TODO: Delete related resources (match-round-links)
    return {"ok": True}
