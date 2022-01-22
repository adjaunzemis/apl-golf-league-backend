from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select


from ..dependencies import get_session
from ..models.flight import Flight, FlightCreate, FlightUpdate, FlightRead, FlightReadWithData, FlightDataWithCount
from ..models.division import Division, DivisionCreate, DivisionUpdate, DivisionRead
from ..models.team import Team, TeamCreate, TeamUpdate, TeamRead
from ..models.query_helpers import TeamWithMatchData, compute_golfer_statistics_for_matches, get_divisions_in_flights, get_flights, get_matches_for_teams, get_team_golfers_for_teams, get_teams_in_flights
from ..models.team_golfer_link import TeamGolferLink

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
    team_golfer_data = get_team_golfers_for_teams(session=session, team_ids=[t.team_id for t in team_data])
    for t in team_data:
        t.golfers = [g for g in team_golfer_data if g.team_id == t.team_id]
    
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
    team_matches = get_matches_for_teams(session=session, team_ids=(team_id,))
    team_golfers = get_team_golfers_for_teams(session=session, team_ids=(team_id,))
    for golfer in team_golfers:
        golfer.statistics = compute_golfer_statistics_for_matches(golfer.golfer_id, team_matches)
    return TeamWithMatchData(
        team_id=team_query_data[0].id,
        flight_id=team_query_data[0].flight_id,
        name=team_query_data[0].name,
        golfers=team_golfers,
        matches=team_matches
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

# TODO: Move team-golfer links to golfers router, or other?
@router.get("/teams/golfers/", response_model=List[TeamGolferLink])
async def read_team_golfer_links(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(TeamGolferLink).offset(offset).limit(limit)).all()

@router.get("/teams/{team_id}/golfers/", response_model=List[TeamGolferLink])
async def read_team_golfer_links_for_team(*, session: Session = Depends(get_session), team_id: int):
    return session.exec(select(TeamGolferLink).where(TeamGolferLink.team_id == team_id)).all()

# @router.post("/teams/{team_id}/golfers/{golfer_id}", response_model=TeamGolferLink)
# async def create_team_golfer_link(*, session: Session = Depends(get_session), team_id: int, golfer_id: int, division_id: int, role: str):
#     link_db = TeamGolferLink(team_id=team_id, golfer_id=golfer_id)
#     session.add(link_db)
#     session.commit()
#     session.refresh(link_db)
#     return link_db

@router.delete("/teams/{team_id}/golfers/{golfer_id}")
async def delete_match_round_link(*, session: Session = Depends(get_session), team_id: int, golfer_id: int):
    link_db = session.get(TeamGolferLink, [team_id, golfer_id])
    if not link_db:
        raise HTTPException(status_code=404, detail="Team-golfer link not found")
    session.delete(link_db)
    session.commit()
    return {"ok": True}
