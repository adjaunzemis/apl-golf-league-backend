from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.tournament import Tournament, TournamentCreate, TournamentUpdate, TournamentRead
from ..models.tournament_division_link import TournamentDivisionLink
from ..models.tournament_team_link import TournamentTeamLink
from ..models.query_helpers import TournamentData, TournamentDataWithCount, get_rounds_for_tournament, get_tournaments, get_divisions_in_tournaments, get_teams_in_tournaments

router = APIRouter(
    prefix="/tournaments",
    tags=["Tournaments"]
)

@router.get("/", response_model=TournamentDataWithCount)
async def read_tournaments(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # TODO: Process query parameters to further limit tournament results returned from database
    tournament_ids = session.exec(select(Tournament.id).offset(offset).limit(limit)).all()
    tournament_data = get_tournaments(session=session, tournament_ids=tournament_ids)
    # Add division and team data to tournament data
    division_data = get_divisions_in_tournaments(session=session, tournament_ids=tournament_ids)
    team_data = get_teams_in_tournaments(session=session, tournament_ids=tournament_ids)
    for tournament in tournament_data:
        tournament.divisions = [d for d in division_data if d.tournament_id == tournament.tournament_id]
        tournament.teams = [t for t in team_data if t.tournament_id == tournament.tournament_id]
    # Return count of relevant tournaments from database and tournament data list
    return TournamentDataWithCount(num_tournaments=len(tournament_ids), tournaments=tournament_data)

@router.post("/", response_model=TournamentRead)
async def create_tournament(*, session: Session = Depends(get_session), tournament: TournamentCreate):
    tournament_db = Tournament.from_orm(tournament)
    session.add(tournament_db)
    session.commit()
    session.refresh(tournament_db)
    return tournament_db

@router.get("/{tournament_id}", response_model=TournamentData)
async def read_tournament(*, session: Session = Depends(get_session), tournament_id: int):
    # Query database for selected tournament, error if not found
    tournament_data = get_tournaments(session=session, tournament_ids=(tournament_id,))
    if (not tournament_data) or (len(tournament_data) == 0):
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament_data = tournament_data[0]
    # Add division and team data to selected tournament
    tournament_data.divisions = get_divisions_in_tournaments(session=session, tournament_ids=(tournament_id,))
    tournament_data.teams = get_teams_in_tournaments(session=session, tournament_ids=(tournament_id,))
    # Compile round data and add to selected tournament teams
    round_data = get_rounds_for_tournament(session=session, tournament_id=tournament_id)
    for team in tournament_data.teams:
        team.rounds = [round for round in round_data if round.team_id == team.id]
        print(f"Team {team.name} has {len(team.rounds)} rounds")
    return tournament_data

@router.patch("/{tournament_id}", response_model=TournamentRead)
async def update_tournament(*, session: Session = Depends(get_session), tournament_id: int, tournament: TournamentUpdate):
    tournament_db = session.get(Tournament, tournament_id)
    if not tournament_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament_data = tournament.dict(exclude_unset=True)
    for key, value in tournament_data.items():
        setattr(tournament_db, key, value)
    session.add(tournament_db)
    session.commit()
    session.refresh(tournament_db)
    return tournament_db

@router.delete("/{tournament_id}")
async def delete_tournament(*, session: Session = Depends(get_session), tournament_id: int):
    tournament_db = session.get(Tournament, tournament_id)
    if not tournament_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    session.delete(tournament_db)
    session.commit()
    return {"ok": True}

@router.get("/division-links/", response_model=List[TournamentDivisionLink])
async def read_tournament_division_links(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(TournamentDivisionLink).offset(offset).limit(limit)).all()

@router.get("/{tournament_id}/division-links/", response_model=List[TournamentDivisionLink])
async def read_tournament_division_links_for_flight(*, session: Session = Depends(get_session), tournament_id: int):
    return session.exec(select(TournamentDivisionLink).where(TournamentDivisionLink.tournament_id == tournament_id)).all()

@router.post("/{tournament_id}/division-links/{division_id}", response_model=TournamentDivisionLink)
async def create_tournament_division_link(*, session: Session = Depends(get_session), tournament_id: int, division_id: int):
    link_db = TournamentDivisionLink(tournament_id=tournament_id, division_id=division_id)
    session.add(link_db)
    session.commit()
    session.refresh(link_db)
    return link_db

@router.delete("/{tournament_id}/division-links/{division_id}")
async def delete_tournament_division_link(*, session: Session = Depends(get_session), tournament_id: int, division_id: int):
    link_db = session.get(TournamentDivisionLink, [tournament_id, division_id])
    if not link_db:
        raise HTTPException(status_code=404, detail="Tournament-division link not found")
    session.delete(link_db)
    session.commit()
    return {"ok": True}

@router.get("/team-links/", response_model=List[TournamentTeamLink])
async def read_tournament_team_links(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(TournamentTeamLink).offset(offset).limit(limit)).all()

@router.get("/{tournament_id}/team-links/", response_model=List[TournamentTeamLink])
async def read_tournament_team_links_for_flight(*, session: Session = Depends(get_session), tournament_id: int):
    return session.exec(select(TournamentTeamLink).where(TournamentTeamLink.tournament_id == tournament_id)).all()

@router.post("/{tournament_id}/team-links/{team_id}", response_model=TournamentTeamLink)
async def create_tournament_team_link(*, session: Session = Depends(get_session), tournament_id: int, team_id: int):
    link_db = TournamentTeamLink(tournament_id=tournament_id, team_id=team_id)
    session.add(link_db)
    session.commit()
    session.refresh(link_db)
    return link_db

@router.delete("/{tournament_id}/team-links/{team_id}")
async def delete_tournament_team_link(*, session: Session = Depends(get_session), tournament_id: int, team_id: int):
    link_db = session.get(TournamentTeamLink, [tournament_id, team_id])
    if not link_db:
        raise HTTPException(status_code=404, detail="Flight-team link not found")
    session.delete(link_db)
    session.commit()
    return {"ok": True}
