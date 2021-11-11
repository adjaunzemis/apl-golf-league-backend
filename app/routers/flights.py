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
    prefix="/flights",
    tags=["Flights"]
)

@router.get("/", response_model=FlightDataWithCount)
async def read_flights(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # TODO: Process query parameters to further limit flight results returned from database
    num_flights = len(session.exec(select(Flight.id)).all())
    flight_query_data = session.exec(select(Flight, Course).join(Course).offset(offset).limit(limit).order_by(Flight.year))

    # Reformat flight data
    if num_flights == 0:
        return FlightDataWithCount(num_flights=0, flights=[])
    
    flight_data = [FlightData(
        flight_id=flight.id,
        year=flight.year,
        name=flight.name,
        home_course_name=home_course.name
    ) for flight, home_course in flight_query_data]
    flight_ids = [f.flight_id for f in flight_data]

    # Query division data for selected flights
    division_query_data = session.exec(select(Division, Tee).join(Tee).where(Division.flight_id.in_(flight_ids)))
    division_data = [DivisionData(
        division_id=division.id,
        flight_id=division.flight_id,
        name=division.name,
        gender=division.gender,
        home_tee_name=home_tee.name,
        home_tee_rating=home_tee.rating,
        home_tee_slope=home_tee.slope
    ) for division, home_tee in division_query_data]

    # Query team data for selected flights
    team_query_data = session.exec(select(Team).where(Team.flight_id.in_(flight_ids)))
    team_data = [TeamData(
        team_id=team.id,
        flight_id=team.flight_id,
        name=team.name
    ) for team in team_query_data]
    team_ids = [t.team_id for t in team_data]

    # Query player data for selected teams
    player_query_data = session.exec(select(Player, Team, Golfer, Division).join(Team).join(Golfer).join(Division).where(Player.team_id.in_(team_ids)))
    player_data = [PlayerData(
        player_id=player.id,
        team_id=player.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        division_name=division.name,
        team_name=team.name,
        role=player.role
    ) for player, team, golfer, division in player_query_data]

    # Add player data to team data
    for t in team_data:
        t.players = [p for p in player_data if p.team_id == t.team_id]
    
    # Add division and team data to flight data
    for f in flight_data:
        f.divisions = [d for d in division_data if d.flight_id == f.flight_id]
        f.teams = [t for t in team_data if t.flight_id == f.flight_id]

    # Return count of relevant flights from database and flight data list
    return FlightDataWithCount(num_flights=num_flights, flights=flight_data)

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

@router.get("/teams/{team_id}", response_model=TeamReadWithPlayers)
async def read_team(*, session: Session = Depends(get_session), team_id: int):
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    return team_db

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

@router.get("/matches/", response_model=List[MatchRead])
async def read_matches(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Match).offset(offset).limit(limit)).all()

@router.post("/matches/", response_model=MatchRead)
async def create_match(*, session: Session = Depends(get_session), match: MatchCreate):
    match_db = Match.from_orm(match)
    session.add(match_db)
    session.commit()
    session.refresh(match_db)
    return match_db

@router.get("/matches/{match_id}", response_model=MatchReadWithData)
async def read_match(*, session: Session = Depends(get_session), match_id: int):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Match not found")
    return match_db

@router.patch("/matches/{match_id}", response_model=MatchRead)
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

@router.delete("/matches/{match_id}")
async def delete_match(*, session: Session = Depends(get_session), match_id: int):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Match not found")
    session.delete(match_db)
    session.commit()
    return {"ok": True}

@router.get("/matches/rounds/", response_model=List[MatchRoundLink])
async def read_match_round_links(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(MatchRoundLink).offset(offset).limit(limit)).all()

@router.get("/matches/{match_id}/rounds/", response_model=List[MatchRoundLink])
async def read_match_round_links_for_match(*, session: Session = Depends(get_session), match_id: int):
    return session.exec(select(MatchRoundLink).where(MatchRoundLink.match_id == match_id)).all()

@router.post("/matches/{match_id}/rounds/{round_id}", response_model=MatchRoundLink)
async def create_match_round_link(*, session: Session = Depends(get_session), match_id: int, round_id: int):
    link_db = MatchRoundLink(match_id=match_id, round_id=round_id)
    session.add(link_db)
    session.commit()
    session.refresh(link_db)
    return link_db

@router.delete("/matches/{match_id}/rounds/{round_id}")
async def delete_match_round_link(*, session: Session = Depends(get_session), match_id: int, round_id: int):
    link_db = session.get(MatchRoundLink, [match_id, round_id])
    if not link_db:
        raise HTTPException(status_code=404, detail="Match-Round link not found")
    session.delete(link_db)
    session.commit()
    return {"ok": True}
