from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from http import HTTPStatus
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_sql_db_session
from ..models.flight import Flight, FlightCreate, FlightUpdate, FlightRead
from ..models.division import Division
from ..models.flight_division_link import FlightDivisionLink
from ..models.match import MatchSummary
from ..models.user import User
from ..models.query_helpers import (
    FlightData,
    FlightInfoWithCount,
    get_divisions_in_flights,
    get_flights,
    get_matches_for_teams,
    get_teams_in_flights,
)

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get("/", response_model=FlightInfoWithCount)
async def read_flights(
    *,
    session: Session = Depends(get_sql_db_session),
    year: int = Query(default=None, ge=2000)
):
    if year:  # filter to a certain year
        flight_ids = session.exec(select(Flight.id).where(Flight.year == year)).all()
    else:  # get all
        flight_ids = session.exec(select(Flight.id)).all()
    flight_info = get_flights(session=session, flight_ids=flight_ids)
    return FlightInfoWithCount(num_flights=len(flight_ids), flights=flight_info)


@router.post("/", response_model=FlightRead)
async def create_flight(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight: FlightCreate
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to create flights",
        )

    # TODO: Sanity-check division tees against flight home-course tees

    # Add flight to database
    flight_db: Flight = Flight.from_orm(flight)
    session.add(flight_db)
    session.commit()
    session.refresh(flight_db)

    # Add divisions and flight-division links to database
    for division in flight.divisions:
        division_db: Division = Division.from_orm(division)
        session.add(division_db)
        session.commit()
        session.refresh(division_db)

        flight_division_link_db = FlightDivisionLink(
            flight_id=flight_db.id, division=division_db.id
        )
        session.add(flight_division_link_db)
        session.commit()
        session.refresh(flight_division_link_db)

    return flight_db


@router.get("/{flight_id}", response_model=FlightData)
async def read_flight(
    *, session: Session = Depends(get_sql_db_session), flight_id: int
):
    # Query database for selected flight, error if not found
    flight_data = get_flights(session=session, flight_ids=(flight_id,))
    if (not flight_data) or (len(flight_data) == 0):
        raise HTTPException(status_code=404, detail="Flight not found")
    flight_data = flight_data[0]
    # Add division and team data to selected flight
    flight_data.divisions = get_divisions_in_flights(
        session=session, flight_ids=(flight_id,)
    )
    flight_data.teams = get_teams_in_flights(session=session, flight_ids=(flight_id,))
    # Compile match summary data and add to selected flight
    team_matches = get_matches_for_teams(
        session=session, team_ids=[t.id for t in flight_data.teams]
    )
    flight_data.matches = [
        MatchSummary(
            match_id=match.match_id,
            home_team_id=match.home_team_id,
            home_team_name=match.home_team_name,
            away_team_id=match.away_team_id,
            away_team_name=match.away_team_name,
            flight_name=match.flight_name,
            week=match.week,
            home_score=match.home_score,
            away_score=match.away_score,
        )
        for match in team_matches
    ]
    return flight_data


@router.patch("/{flight_id}", response_model=FlightRead)
async def update_flight(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight_id: int,
    flight: FlightUpdate
):
    if not (current_user.edit_flights or current_user.is_admin):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to update flights",
        )
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
async def delete_flight(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight_id: int
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to delete flights",
        )
    flight_db = session.get(Flight, flight_id)
    if not flight_db:
        raise HTTPException(status_code=404, detail="Flight not found")
    session.delete(flight_db)
    session.commit()
    # TODO: Delete linked resources (divisions, teams, etc.)
    return {"ok": True}
