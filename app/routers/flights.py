from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select, SQLModel
import numpy as np

from ..dependencies import get_session
from ..models.flight import Flight, FlightCreate, FlightUpdate, FlightRead, FlightReadWithData, FlightData, FlightDataWithCount
from ..models.division import Division, DivisionCreate, DivisionUpdate, DivisionRead, DivisionData
from ..models.team import Team, TeamCreate, TeamUpdate, TeamRead, TeamData
from ..models.player import Player, PlayerCreate, PlayerUpdate, PlayerRead, PlayerReadWithData, PlayerData
from ..models.course import Course
from ..models.tee import Tee
from ..models.golfer import Golfer
from ..models.match import Match, MatchData
from ..models.match_round_link import MatchRoundLink
from ..models.round import Round, RoundData
from ..models.track import Track
from ..models.hole import Hole
from ..models.hole_result import HoleResult, HoleResultData
from ..utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

router = APIRouter(
    prefix="/flights",
    tags=["Flights"]
)

# TODO: Move data models to separate class?
class TeamWithMatchData(SQLModel):
    team_id: int
    flight_id: int
    name: str
    players: List[PlayerData] = []
    matches: List[MatchData] = []

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

@router.get("/teams/{team_id}", response_model=TeamWithMatchData)
async def read_team(*, session: Session = Depends(get_session), team_id: int):
    # Query team data
    team_query_data = session.exec(select(Team, Flight).join(Flight).where(Team.id == team_id)).all()
    if not team_query_data:
        raise HTTPException(status_code=404, detail="Team not found")

    team_query_data = team_query_data[0]
    team_data = TeamWithMatchData(
        team_id=team_query_data[0].id,
        flight_id=team_query_data[0].flight_id,
        name=team_query_data[0].name
    )
    flight_name = team_query_data[1].name

    # Query player data for selected team
    player_query_data = session.exec(select(Player, Team, Golfer, Division).join(Team).join(Golfer).join(Division).where(Player.team_id == team_id))
    team_data.players = [PlayerData(
        player_id=player.id,
        team_id=player.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        flight_name=flight_name,
        division_name=division.name,
        team_name=team.name,
        role=player.role
    ) for player, team, golfer, division in player_query_data]

    # Query match data for selected team
    match_query_data = session.exec(select(Match).where((Match.home_team_id == team_id) | (Match.away_team_id == team_id))).all()
    match_data = [MatchData(
        match_id=match.id,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        flight_name=flight_name,
        week=match.week,
        home_score=match.home_score,
        away_score=match.away_score
    ) for match in match_query_data]
    match_ids = [m.match_id for m in match_data]

    # Query round data for selected matches
    round_query_data = session.exec(select(Round, MatchRoundLink, Golfer, Course, Tee, Team).join(MatchRoundLink, onclause=MatchRoundLink.round_id == Round.id).join(Match, onclause=Match.id == MatchRoundLink.match_id).join(Tee).join(Track).join(Course).join(Golfer).join(Player, ((Player.golfer_id == Round.golfer_id) & (Player.team_id.in_((Match.home_team_id, Match.away_team_id))))).join(Team, onclause=Player.team_id == Team.id).where(MatchRoundLink.match_id.in_(match_ids)))
    round_data = [RoundData(
        round_id=round.id,
        match_id=match_round_link.match_id,
        team_id=team.id,
        date_played=round.date_played,
        golfer_name=golfer.name,
        golfer_handicap_index=round.handicap_index,
        golfer_playing_handicap=round.playing_handicap,
        team_name=team.name,
        course_name=course.name,
        tee_name=tee.name,
        tee_gender=tee.gender,
        tee_rating=tee.rating,
        tee_slope=tee.slope,
        tee_color=tee.color if tee.color else "none",
    ) for round, match_round_link, golfer, course, tee, team in round_query_data]
    round_ids = [r.round_id for r in round_data]

    # Query hole data for selected rounds
    hole_query_data = session.exec(select(HoleResult, Hole).join(Hole).where(HoleResult.round_id.in_(round_ids)))
    hole_result_data = [HoleResultData(
        hole_result_id=hole_result.id,
        round_id=hole_result.round_id,
        hole_id=hole_result.hole_id,
        number=hole.number,
        par=hole.par,
        yardage=hole.yardage,
        stroke_index=hole.stroke_index,
        gross_score=hole_result.strokes
    ) for hole_result, hole in hole_query_data]

    # Add hole data to round data
    # TODO: Compute handicap strokes and non-gross scores on entry to database
    ahs = APLLegacyHandicapSystem()
    for r in round_data:
        r.holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in r.holes])
        r.gross_score = sum([h.gross_score for h in r.holes])
        for h in r.holes:
            h.handicap_strokes = ahs.compute_hole_handicap_strokes(h.stroke_index, r.golfer_playing_handicap)
            h.adjusted_gross_score = ahs.compute_hole_adjusted_gross_score(h.par, h.stroke_index, h.gross_score, course_handicap=r.golfer_playing_handicap)
            h.net_score = h.gross_score - h.handicap_strokes
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in r.holes])
        r.net_score = sum([h.net_score for h in r.holes])

    # Add round data to match data
    for m in match_data:
        m.rounds = [r for r in round_data if r.match_id == m.match_id]

    # Add match data to team data
    team_data.matches = match_data

    # Return team data
    return team_data

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
