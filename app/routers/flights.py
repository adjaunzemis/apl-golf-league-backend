from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.flight import Flight, FlightCreate, FlightUpdate, FlightRead
from ..models.match import MatchSummary
from ..models.flight_team_link import FlightTeamLink
from ..models.query_helpers import FlightData, FlightDataWithCount, get_divisions_in_flights, get_flights, get_matches_for_teams, get_teams_in_flights

router = APIRouter(
    prefix="/flights",
    tags=["Flights"]
)

@router.get("/", response_model=FlightDataWithCount)
async def read_flights(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # TODO: Process query parameters to further limit flight results returned from database
    flight_ids = session.exec(select(Flight.id).offset(offset).limit(limit)).all()
    flight_data = get_flights(session=session, flight_ids=flight_ids)
    # Add division and team data to flight data
    division_data = get_divisions_in_flights(session=session, flight_ids=flight_ids)
    team_data = get_teams_in_flights(session=session, flight_ids=flight_ids)
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

@router.get("/{flight_id}", response_model=FlightData)
async def read_flight(*, session: Session = Depends(get_session), flight_id: int):
    # Query database for selected flight, error if not found
    flight_data = get_flights(session=session, flight_ids=(flight_id,))
    if (not flight_data) or (len(flight_data) == 0):
        raise HTTPException(status_code=404, detail="Flight not found")
    flight_data = flight_data[0]
    # Add division and team data to selected flight
    flight_data.divisions = get_divisions_in_flights(session=session, flight_ids=(flight_id,))
    flight_data.teams = get_teams_in_flights(session=session, flight_ids=(flight_id,))
    # Compile match summary data and add to selected flight 
    team_matches = get_matches_for_teams(session=session, team_ids=[t.id for t in flight_data.teams])
    flight_data.matches = [MatchSummary(
            match_id=match.match_id,
            home_team_id=match.home_team_id,
            home_team_name=match.home_team_name,
            away_team_id=match.away_team_id,
            away_team_name=match.away_team_name,
            flight_name=match.flight_name,
            week=match.week,
            home_score=match.home_score,
            away_score=match.away_score
        ) for match in team_matches]
    return flight_data

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

@router.get("/team-links/", response_model=List[FlightTeamLink])
async def read_flight_team_links(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(FlightTeamLink).offset(offset).limit(limit)).all()

@router.get("/{flight_id}/team-links/", response_model=List[FlightTeamLink])
async def read_flight_team_links_for_flight(*, session: Session = Depends(get_session), flight_id: int):
    return session.exec(select(FlightTeamLink).where(FlightTeamLink.flight_id == flight_id)).all()

@router.post("/{flight_id}/team-links/{team_id}", response_model=FlightTeamLink)
async def create_flight_team_link(*, session: Session = Depends(get_session), flight_id: int, team_id: int):
    link_db = FlightTeamLink(flight_id=flight_id, team_id=team_id)
    session.add(link_db)
    session.commit()
    session.refresh(link_db)
    return link_db

@router.delete("/{flight_id}/team-links/{team_id}")
async def delete_flight_team_link(*, session: Session = Depends(get_session), flight_id: int, team_id: int):
    link_db = session.get(FlightTeamLink, [flight_id, team_id])
    if not link_db:
        raise HTTPException(status_code=404, detail="Flight-team link not found")
    session.delete(link_db)
    session.commit()
    return {"ok": True}
