from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.team import Team, TeamCreate, TeamUpdate, TeamRead
from ..models.team_golfer_link import TeamGolferLink
from ..models.query_helpers import TeamWithMatchData, compute_golfer_statistics_for_matches, get_team_golfers_for_teams, get_matches_for_teams

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)

@router.get("/", response_model=List[TeamRead])
async def read_teams(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Team).offset(offset).limit(limit)).all()

@router.post("/", response_model=TeamRead)
async def create_team(*, session: Session = Depends(get_session), team: TeamCreate):
    team_db = Team.from_orm(team)
    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    return team_db

@router.get("/{team_id}", response_model=TeamWithMatchData)
async def read_team(*, session: Session = Depends(get_session), team_id: int):
    team_db = session.exec(select(Team).where(Team.id == team_id)).one_or_none()
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    team_matches = get_matches_for_teams(session=session, team_ids=(team_id,))
    team_golfers = get_team_golfers_for_teams(session=session, team_ids=(team_id,))
    for golfer in team_golfers:
        golfer.statistics = compute_golfer_statistics_for_matches(golfer.golfer_id, team_matches)
    return TeamWithMatchData(
        id=team_db.id,
        name=team_db.name,
        year=team_golfers[0].year,
        golfers=team_golfers,
        matches=team_matches
    )

@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(*, session: Session = Depends(get_session), team_id: int, team: TeamUpdate):
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.dict(exclude_unset=True)
    for key, value in team_data.items():
        setattr(team_db, key, value)
    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    return team_db

@router.delete("/{team_id}")
async def delete_team(*, session: Session = Depends(get_session), team_id: int):
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team_db)
    session.commit()
    return {"ok": True}

@router.get("/golfer-links/", response_model=List[TeamGolferLink])
async def read_team_golfer_links(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(TeamGolferLink).offset(offset).limit(limit)).all()

@router.get("/{team_id}/golfer-links/", response_model=List[TeamGolferLink])
async def read_team_golfer_links_for_team(*, session: Session = Depends(get_session), team_id: int):
    return session.exec(select(TeamGolferLink).where(TeamGolferLink.team_id == team_id)).all()

@router.post("/{team_id}/golfer-links/{golfer_id}", response_model=TeamGolferLink)
async def create_team_golfer_link(*, session: Session = Depends(get_session), team_id: int, golfer_id: int, division_id: int = Query(default=None), role: str = Query(default="Player")):
    link_db = TeamGolferLink(team_id=team_id, golfer_id=golfer_id, division_id=division_id, role=role)
    session.add(link_db)
    session.commit()
    session.refresh(link_db)
    return link_db

@router.delete("/{team_id}/golfer-links/{golfer_id}")
async def delete_team_golfer_link(*, session: Session = Depends(get_session), team_id: int, golfer_id: int):
    link_db = session.get(TeamGolferLink, [team_id, golfer_id])
    if not link_db:
        raise HTTPException(status_code=404, detail="Team-golfer link not found")
    session.delete(link_db)
    session.commit()
    return {"ok": True}
