from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_session
from ..models.flight import Flight, FlightCreate, FlightUpdate, FlightRead
from ..models.match import MatchSummary
from ..models.user import User
from ..models.payment import LeagueDuesPayment, LeagueDuesPaymentRead, LeagueDuesType
from ..models.query_helpers import FlightData, FlightInfoWithCount, get_divisions_in_flights, get_flights, get_matches_for_teams, get_teams_in_flights

router = APIRouter(
    prefix="/flights",
    tags=["Flights"]
)

@router.get("/", response_model=FlightInfoWithCount)
async def read_flights(*, session: Session = Depends(get_session), year: int = Query(default=None, ge=2000)):
    if year: # filter to a certain year
        flight_ids = session.exec(select(Flight.id).where(Flight.year == year)).all()
    else: # get all
        flight_ids = session.exec(select(Flight.id)).all()
    flight_info = get_flights(session=session, flight_ids=flight_ids)
    return FlightInfoWithCount(num_flights=len(flight_ids), flights=flight_info)

@router.post("/", response_model=FlightRead)
async def create_flight(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), flight: FlightCreate):
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
async def update_flight(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), flight_id: int, flight: FlightUpdate):
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
async def delete_flight(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), flight_id: int):
    flight_db = session.get(Flight, flight_id)
    if not flight_db:
        raise HTTPException(status_code=404, detail="Flight not found")
    session.delete(flight_db)
    session.commit()
    # TODO: Delete linked resources (divisions, teams, etc.)
    return {"ok": True}

@router.get("/payments", response_model=List[LeagueDuesPaymentRead])
async def read_flight_payments(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), year: int):
    flight_payments_db = session.exec(select(LeagueDuesPayment).where(LeagueDuesPayment.type == LeagueDuesType.FLIGHT_DUES).where(LeagueDuesPayment.year == year)).all()
    if not flight_payments_db:
        raise HTTPException(status_code=404, detail=f"No flight dues payment information found for year: {year}")
    return flight_payments_db
