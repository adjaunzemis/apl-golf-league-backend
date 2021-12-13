from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.flight import Flight, FlightCreate, FlightUpdate, FlightRead, FlightReadWithData, FlightDataWithCount
from ..models.division import Division, DivisionCreate, DivisionUpdate, DivisionRead
from ..models.team import Team, TeamCreate, TeamUpdate, TeamRead
from ..models.player import Player, PlayerCreate, PlayerUpdate, PlayerRead, PlayerReadWithData, PlayerData
from ..models.query_helpers import TeamWithMatchData, get_divisions_in_flights, get_flights, get_matches_for_teams, get_players_in_teams, get_teams_in_flights

router = APIRouter(
    prefix="/flights",
    tags=["Flights"]
)

@router.get("/", response_model=FlightDataWithCount)
async def read_flights(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # TODO: Process query parameters to further limit flight results returned from database
    flight_ids = session.exec(select(Flight.id).offset(offset).limit(limit)).all()
    flight_data = get_flights(session=session, flight_ids=flight_ids)

    # Get division data for selected flights
    division_data = get_divisions_in_flights(session=session, flight_ids=flight_ids)

    # Get team and player data for selected flights
    team_data = get_teams_in_flights(session=session, flight_ids=flight_ids)
    player_data = get_players_in_teams(session=session, team_ids=[t.team_id for t in team_data])
    for t in team_data:
        t.players = [p for p in player_data if p.team_id == t.team_id]
    
    # Add division and team data to flight data
    for f in flight_data:
        f.divisions = [d for d in division_data if d.flight_id == f.flight_id]
        f.teams = [t for t in team_data if t.flight_id == f.flight_id]

    # Return count of relevant flights from database and flight data list
    return FlightDataWithCount(num_flights=len(flight_ids), flights=flight_data)

@router.post("/", response_model=FlightRead)
async def create_flight(*, session: Session = Depends(get_session), flight: FlightCreate):
    flight_db = Flight.from_orm(flight)
    session.add(flight_db)
    session.commit()
    session.refresh(flight_db)
    return flight_db

@router.get("/{flight_id}", response_model=FlightReadWithData)
async def read_flight(*, session: Session = Depends(get_session), flight_id: int):
    flight_db = session.get(Flight, flight_id)
    if not flight_db:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight_db

@router.patch("/{flight_id}", response_model=FlightRead)
async def update_flight(*, session: Session = Depends(get_session), flight_id: int, flight: FlightUpdate):
    flight_db = session.get(Flight, flight_id)
    if not flight_db:
        raise HTTPException(status_code=404, detail="Flight not found")
    flight_data = flight.dict(exclude_unset=True)
    for key, value in flight_data.items():
        setattr(flight_db, key, value)
    session.add(flight_db)
    session.commit()
    session.refresh(flight_db)
    return flight_db

@router.delete("/{flight_id}")
async def delete_flight(*, session: Session = Depends(get_session), flight_id: int):
    flight_db = session.get(Flight, flight_id)
    if not flight_db:
        raise HTTPException(status_code=404, detail="Flight not found")
    session.delete(flight_db)
    session.commit()
    return {"ok": True}

@router.get("/divisions/", response_model=List[DivisionRead])
async def read_divisions(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Division).offset(offset).limit(limit)).all()

@router.post("/divisions/", response_model=DivisionRead)
async def create_division(*, session: Session = Depends(get_session), division: DivisionCreate):
    division_db = Division.from_orm(division)
    session.add(division_db)
    session.commit()
    session.refresh(division_db)
    return division_db

@router.get("/divisions/{division_id}", response_model=DivisionRead)
async def read_division(*, session: Session = Depends(get_session), division_id: int):
    division_db = session.get(Division, division_id)
    if not division_db:
        raise HTTPException(status_code=404, detail="Division not found")
    return division_db

@router.patch("/divisions/{division_id}", response_model=DivisionRead)
async def update_division(*, session: Session = Depends(get_session), division_id: int, division: DivisionUpdate):
    division_db = session.get(Division, division_id)
    if not division_db:
        raise HTTPException(status_code=404, detail="Division not found")
    division_data = division.dict(exclude_unset=True)
    for key, value in division_data.items():
        setattr(division_db, key, value)
    session.add(division_db)
    session.commit()
    session.refresh(division_db)
    return division_db

@router.delete("/divisions/{division_id}")
async def delete_division(*, session: Session = Depends(get_session), division_id: int):
    division_db = session.get(Division, division_id)
    if not division_db:
        raise HTTPException(status_code=404, detail="Division not found")
    session.delete(division_db)
    session.commit()
    return {"ok": True}

@router.get("/teams/", response_model=List[TeamRead])
async def read_teams(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Team).offset(offset).limit(limit)).all()

@router.post("/teams/", response_model=TeamRead)
async def create_team(*, session: Session = Depends(get_session), team: TeamCreate):
    team_db = Team.from_orm(team)
    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    return team_db

@router.get("/teams/{team_id}", response_model=TeamWithMatchData)
async def read_team(*, session: Session = Depends(get_session), team_id: int):
    team_query_data = session.exec(select(Team).where(Team.id == team_id)).all()
    if not team_query_data:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamWithMatchData(
        team_id=team_query_data[0].id,
        flight_id=team_query_data[0].flight_id,
        name=team_query_data[0].name,
        players=get_players_in_teams(session=session, team_ids=(team_id,)),
        matches=get_matches_for_teams(session=session, team_ids=(team_id,))
    )

@router.patch("/teams/{team_id}", response_model=TeamRead)
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

@router.delete("/teams/{team_id}")
async def delete_team(*, session: Session = Depends(get_session), team_id: int):
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team_db)
    session.commit()
    return {"ok": True}

@router.get("/players/", response_model=List[PlayerRead])
async def read_players(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Player).offset(offset).limit(limit)).all()

@router.post("/players/", response_model=PlayerRead)
async def create_player(*, session: Session = Depends(get_session), player: PlayerCreate):
    player_db = Player.from_orm(player)
    session.add(player_db)
    session.commit()
    session.refresh(player_db)
    return player_db

@router.get("/players/{player_id}", response_model=PlayerReadWithData)
async def read_player(*, session: Session = Depends(get_session), player_id: int):
    player_db = session.get(Player, player_id)
    if not player_db:
        raise HTTPException(status_code=404, detail="Player not found")
    return player_db

@router.patch("/players/{player_id}", response_model=PlayerRead)
async def update_player(*, session: Session = Depends(get_session), player_id: int, player: PlayerUpdate):
    player_db = session.get(Player, player_id)
    if not player_db:
        raise HTTPException(status_code=404, detail="Player not found")
    player_data = player.dict(exclude_unset=True)
    for key, value in player_data.items():
        setattr(player_db, key, value)
    session.add(player_db)
    session.commit()
    session.refresh(player_db)
    return player_db

@router.delete("/players/{player_id}")
async def delete_player(*, session: Session = Depends(get_session), player_id: int):
    player_db = session.get(Player, player_id)
    if not player_db:
        raise HTTPException(status_code=404, detail="Player not found")
    session.delete(player_db)
    session.commit()
    return {"ok": True}
