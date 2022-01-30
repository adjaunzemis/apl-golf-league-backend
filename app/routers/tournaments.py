from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.tournament import Tournament, TournamentCreate, TournamentUpdate, TournamentRead
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
