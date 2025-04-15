from http import HTTPStatus

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.exceptions import HTTPException
from pydantic.v1 import BaseModel
from sqlmodel import Session, select

from app.database import flights as db_flights
from app.database import teams as db_teams
from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.flight import Flight, FlightCreate, FlightInfo, FlightRead
from app.models.flight_division_link import FlightDivisionLink
from app.models.flight_team_link import FlightTeamLink
from app.models.match import MatchSummary
from app.models.query_helpers import (
    FlightData,
    get_divisions_in_flights,
    get_flights,
    get_matches_for_teams,
    get_teams_in_flights,
)
from app.models.team_golfer_link import TeamGolferLink
from app.models.user import User
from app.routers.utilities import upsert_division

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get("/", response_model=list[FlightInfo])
async def read_flights(
    *,
    session: Session = Depends(get_sql_db_session),
    year: int = Query(default=None, ge=2000),
):
    flight_ids = db_flights.get_ids(session=session, year=year)
    infos = [
        db_flights.get_info(session=session, flight_id=flight_id)
        for flight_id in flight_ids
    ]
    return sorted(infos, key=lambda info: info.name)


@router.get("/{flight_id}", response_model=FlightData)
async def read_flight(
    *, session: Session = Depends(get_sql_db_session), flight_id: int
):
    # Query database for selected flight, error if not found
    flight_data = get_flights(session=session, flight_ids=(flight_id,))
    if (not flight_data) or (len(flight_data) == 0):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Flight not found")
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


@router.post("/", response_model=FlightRead)
async def create_flight(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight: FlightCreate,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to create flights",
        )

    # TODO: Validate flight data (e.g. division tees against flight home-course tees)

    return upsert_flight(session=session, flight_data=flight)


@router.put("/{flight_id}", response_model=FlightRead)
async def update_flight(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight_id: int,
    flight: FlightCreate,
):
    if not (current_user.edit_flights or current_user.is_admin):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to update flights",
        )

    flight_db = session.get(Flight, flight_id)
    if not flight_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Flight not found")

    # TODO: Validate flight data (e.g. division tees against flight home-course tees)

    return upsert_flight(session=session, flight_data=flight)


@router.delete("/{flight_id}")
async def delete_flight(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight_id: int,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to delete flights",
        )
    flight_db = session.get(Flight, flight_id)
    if not flight_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Flight not found")
    session.delete(flight_db)
    session.commit()
    # TODO: Delete linked resources (divisions, teams, etc.)
    return {"ok": True}


def upsert_flight(*, session: Session, flight_data: FlightCreate) -> FlightRead:
    """Updates/inserts a flight data record."""
    if flight_data.id is None:  # create new flight
        flight_db = Flight.model_validate(flight_data)
    else:  # update existing flight
        flight_db = session.get(Flight, flight_data.id)
        if not flight_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Flight (id={flight_data.id}) not found",
            )
        flight_dict = flight_data.model_dump(exclude_unset=True)
        for key, value in flight_dict.items():
            if key != "divisions":
                setattr(flight_db, key, value)
    session.add(flight_db)
    session.commit()
    session.refresh(flight_db)

    for division in flight_data.divisions:
        division_db = upsert_division(session=session, division_data=division)

        # Create flight-division link (if needed)
        flight_division_link_db = session.exec(
            select(FlightDivisionLink)
            .where(FlightDivisionLink.flight_id == flight_db.id)
            .where(FlightDivisionLink.division_id == division_db.id)
        ).one_or_none()
        if not flight_division_link_db:
            flight_division_link_db = FlightDivisionLink(
                flight_id=flight_db.id, division_id=division_db.id
            )
            session.add(flight_division_link_db)
            session.commit()
            session.refresh(flight_division_link_db)

    session.refresh(flight_db)
    return flight_db


@router.get("/info/{flight_id}")
async def get_info(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_flights.get_info(session=session, flight_id=flight_id)


@router.get("/divisions/{flight_id}")
async def get_divisions(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_flights.get_divisions(session=session, flight_id=flight_id)


@router.get("/teams/{flight_id}")
async def get_teams(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_flights.get_teams(session=session, flight_id=flight_id)


@router.get("/substitutes/{flight_id}")
async def get_substitutes(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_flights.get_substitutes(session=session, flight_id=flight_id)


@router.get("/free_agents/{flight_id}")
async def get_free_agents(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_flights.get_free_agents(session=session, flight_id=flight_id)


@router.get("/matches/{flight_id}")
async def get_matches(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_flights.get_match_summaries(session=session, flight_id=flight_id)


@router.get("/standings/{flight_id}")
async def get_standings(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_flights.get_standings(session=session, flight_id=flight_id)


@router.get("/statistics/{flight_id}")
async def get_statistics(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_flights.get_statistics(session=session, flight_id=flight_id)


class MoveTeamRequest(BaseModel):
    team_id: int
    flight_id: int


@router.patch("/move-team")
async def move_team(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    request: MoveTeamRequest,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized to move teams between flights",
        )

    team_db = db_teams.get_by_id(session=session, team_id=request.team_id)
    if team_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    matches_db = db_teams.get_matches(session=session, team_id=request.team_id)
    if len(matches_db) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot move team with allocated matches",
        )

    if team_db.flight.id == request.flight_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Team is already on requested flight",
        )

    new_flight_db = db_flights.get_by_id(session=session, flight_id=request.flight_id)
    if new_flight_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="New flight not found"
        )

    if new_flight_db.year != team_db.flight.year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot move team between flights from different years",
        )

    ftl_db = db_flights.get_team_link(session=session, team_id=team_db.id)
    if ftl_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to link team id={team_db.id} to a flight",
        )
    session.delete(ftl_db)
    session.add(FlightTeamLink(flight_id=new_flight_db.id, team_id=team_db.id))

    tgls_db = session.exec(
        select(TeamGolferLink).where(TeamGolferLink.team_id == request.team_id)
    ).all()

    new_flight_divisions = {
        division_db.name: division_db
        for division_db in db_flights.get_divisions(
            session=session, flight_id=request.flight_id
        )
    }

    team_golfers = {
        golfer_db.golfer_id: golfer_db
        for golfer_db in db_teams.get_golfers(session=session, team_id=request.team_id)
    }

    for tgl_db in tgls_db:
        golfer_db = team_golfers.get(tgl_db.golfer_id)
        if golfer_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to find golfer id={tgl_db.golfer_id} in team id={tgl_db.team_id}",
            )

        new_division_db = new_flight_divisions.get(golfer_db.division_name)
        if new_division_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to find division with name={golfer_db.division_name} in flight id={request.flight_id}",
            )

        session.add(
            TeamGolferLink(
                team_id=team_db.id,
                golfer_id=tgl_db.golfer_id,
                role=tgl_db.role,
                division_id=new_division_db.id,
            )
        )

        session.delete(tgl_db)

    session.commit()
    session.refresh(team_db)
    return team_db
