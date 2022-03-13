from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select


from ..dependencies import get_current_active_user, get_session
from ..models.tournament import Tournament, TournamentCreate, TournamentUpdate, TournamentRead
from ..models.tournament_division_link import TournamentDivisionLink
from ..models.tournament_team_link import TournamentTeamLink
from ..models.user import User
from ..models.query_helpers import TournamentData, TournamentInfoWithCount, get_rounds_for_tournament, get_tournaments, get_divisions_in_tournaments, get_teams_in_tournaments

router = APIRouter(
    prefix="/tournaments",
    tags=["Tournaments"]
)

@router.get("/", response_model=TournamentInfoWithCount)
async def read_tournaments(*, session: Session = Depends(get_session), year: int = Query(default=None, ge=2000)):
    if year: # filter to a certain year
        tournament_ids = session.exec(select(Tournament.id).where(Tournament.year == year)).all()
    else: # get all
        tournament_ids = session.exec(select(Tournament.id)).all()
    tournament_info = get_tournaments(session=session, tournament_ids=tournament_ids)
    return TournamentInfoWithCount(num_tournaments=len(tournament_ids), tournaments=tournament_info)

@router.post("/", response_model=TournamentRead)
async def create_tournament(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), tournament: TournamentCreate):
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
    return tournament_data

@router.patch("/{tournament_id}", response_model=TournamentRead)
async def update_tournament(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), tournament_id: int, tournament: TournamentUpdate):
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
async def delete_tournament(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), tournament_id: int):
    tournament_db = session.get(Tournament, tournament_id)
    if not tournament_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    session.delete(tournament_db)
    session.commit()
    return {"ok": True}
