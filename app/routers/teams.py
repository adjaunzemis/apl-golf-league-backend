import copy
from http import HTTPStatus
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import SQLModel, Session, select


from ..dependencies import get_current_active_user, get_sql_db_session
from ..models.team import Team, TeamCreate, TeamUpdate, TeamRead
from ..models.team_golfer_link import TeamGolferLink, TeamRole
from ..models.golfer import Golfer
from ..models.flight import Flight
from ..models.flight_team_link import FlightTeamLink
from ..models.tournament import Tournament
from ..models.tournament_team_link import TournamentTeamLink
from ..models.payment import (
    LeagueDues,
    LeagueDuesPayment,
    LeagueDuesType,
    TournamentEntryFeePayment,
    TournamentEntryFeeType,
)
from ..models.user import User
from ..models.query_helpers import (
    TeamWithMatchData,
    compute_golfer_statistics_for_matches,
    get_flight_team_golfers_for_teams,
    get_matches_for_teams,
)

router = APIRouter(prefix="/teams", tags=["Teams"])


class TeamGolferSignupData(SQLModel):
    golfer_id: int
    golfer_name: str
    role: str
    division_id: int


class TeamSignupData(SQLModel):
    flight_id: Optional[int] = None
    tournament_id: Optional[int] = None
    name: str
    golfer_data: List[TeamGolferSignupData]


@router.get("/", response_model=List[TeamRead])
async def read_teams(
    *,
    session: Session = Depends(get_sql_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100),
):
    return session.exec(select(Team).offset(offset).limit(limit)).all()


@router.get("/{team_id}", response_model=TeamWithMatchData)
async def read_team(*, session: Session = Depends(get_sql_db_session), team_id: int):
    team_db = session.exec(select(Team).where(Team.id == team_id)).one_or_none()
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    team_matches = get_matches_for_teams(session=session, team_ids=(team_id,))
    team_golfers = get_flight_team_golfers_for_teams(
        session=session, team_ids=(team_id,)
    )
    for golfer in team_golfers:
        golfer.statistics = compute_golfer_statistics_for_matches(
            golfer.golfer_id, team_matches
        )
    return TeamWithMatchData(
        id=team_db.id,
        name=team_db.name,
        year=team_golfers[0].year,
        golfers=team_golfers,
        matches=team_matches,
    )


@router.post("/", response_model=TeamRead)
async def create_team(
    *, session: Session = Depends(get_sql_db_session), team_data: TeamSignupData
):
    # Validate sign-ups
    validate_team_signup_data(session=session, team_data=team_data)

    # Create team
    if team_data.flight_id:
        return create_team_for_flight(session=session, team_data=team_data)
    elif team_data.tournament_id:
        return create_team_for_tournament(session=session, team_data=team_data)
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid team data, must specify flight or tournament id",
        )


@router.put("/{team_id}", response_model=TeamRead)
async def update_team(
    *,
    session: Session = Depends(get_sql_db_session),
    team_id: int,
    team_data: TeamSignupData,
):
    # Check for existing team
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Team not found")

    # Validate sign-ups
    validate_team_signup_data(
        session=session, team_data=team_data, exclude_team_id=team_db.id
    )

    # Update team
    if team_data.flight_id:
        return update_team_for_flight(
            session=session, team_data=team_data, team_db=team_db
        )
    elif team_data.tournament_id:
        return update_team_for_tournament(
            session=session, team_data=team_data, team_db=team_db
        )
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid team data, must specify flight or tournament id",
        )


@router.delete("/{team_id}")
async def delete_team(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    team_id: int,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, defailt="User not allowed to delete teams"
        )

    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")

    # Find and remove all team-golfer links
    team_golfer_links_db = session.exec(
        select(TeamGolferLink).where(TeamGolferLink.team_id == team_id)
    ).all()
    for team_golfer_link_db in team_golfer_links_db:
        print(f"Deleting team-golfer link: golfer_id={team_golfer_link_db.golfer_id}")
        session.delete(team_golfer_link_db)

    # Find and remove all flight-team links
    flight_team_links_db = session.exec(
        select(FlightTeamLink).where(FlightTeamLink.team_id == team_id)
    ).all()
    for flight_team_link_db in flight_team_links_db:
        print(f"Deleting flight-team link: flight_id={flight_team_link_db.flight_id}")
        session.delete(flight_team_link_db)

    # Find and remove all tournament-team links
    tournament_team_links_db = session.exec(
        select(TournamentTeamLink).where(TournamentTeamLink.team_id == team_id)
    ).all()
    for tournament_team_link_db in tournament_team_links_db:
        print(
            f"Deleting tournament-team link: tournament_id={tournament_team_link_db.tournament_id}"
        )
        session.delete(tournament_team_link_db)

    # Remove team
    print(f"Deleting team: id={team_db.id}")
    session.delete(team_db)

    # Commit database changes
    session.commit()
    return {"ok": True}


def validate_team_signup_data(
    *,
    session: Session,
    team_data: TeamSignupData,
    exclude_team_id: Optional[int] = None,
) -> None:
    # Check if flight/tournament selection is valid
    if (team_data.flight_id and team_data.tournament_id) or (
        not team_data.flight_id and not team_data.tournament_id
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f"Invalid team data, must specify exactly one flight or tournament id",
        )

    # Check if team name is valid
    if team_data.flight_id:
        if exclude_team_id is None:
            team_db = session.exec(
                select(Team)
                .join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id)
                .join(Flight, onclause=Flight.id == FlightTeamLink.flight_id)
                .where(Flight.id == team_data.flight_id)
                .where(Team.name == team_data.name)
            ).one_or_none()
        else:
            team_db = session.exec(
                select(Team)
                .join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id)
                .join(Flight, onclause=Flight.id == FlightTeamLink.flight_id)
                .where(Flight.id == team_data.flight_id)
                .where(Team.name == team_data.name)
                .where(Team.id != exclude_team_id)
            ).one_or_none()
        if team_db:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"Team '{team_data.name}' already exists in this flight",
            )
    elif team_data.tournament_id:
        if exclude_team_id is None:
            team_db = session.exec(
                select(Team)
                .join(
                    TournamentTeamLink, onclause=TournamentTeamLink.team_id == Team.id
                )
                .join(
                    Tournament,
                    onclause=Tournament.id == TournamentTeamLink.tournament_id,
                )
                .where(Tournament.id == team_data.tournament_id)
                .where(Team.name == team_data.name)
            ).one_or_none()
        else:
            team_db = session.exec(
                select(Team)
                .join(
                    TournamentTeamLink, onclause=TournamentTeamLink.team_id == Team.id
                )
                .join(
                    Tournament,
                    onclause=Tournament.id == TournamentTeamLink.tournament_id,
                )
                .where(Tournament.id == team_data.tournament_id)
                .where(Team.name == team_data.name)
                .where(Team.id != exclude_team_id)
            ).one_or_none()
        if team_db:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"Team '{team_data.name}' already exists in this tournament",
            )

    # Check for duplicate golfers in signup
    golfer_id_list = [team_golfer.golfer_id for team_golfer in team_data.golfer_data]
    if len(golfer_id_list) != len(set(golfer_id_list)):
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Team '{team_data.name}' contains duplicate golfer sign-ups",
        )

    # Check if the given golfers already exist on other teams in this flight and if one captain was designated
    if team_data.flight_id is not None:
        existing_golfer_ids = get_golfer_ids_for_flight(
            session=session,
            flight_id=team_data.flight_id,
            exclude_team_id=exclude_team_id,
        )
    elif team_data.tournament_id is not None:
        existing_golfer_ids = get_golfer_ids_for_tournament(
            session=session,
            tournament_id=team_data.tournament_id,
            exclude_team_id=exclude_team_id,
        )
    team_has_captain = False
    for team_golfer in team_data.golfer_data:
        if team_golfer.golfer_id in existing_golfer_ids:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=f"Golfer '{team_golfer.golfer_name}' is already on a team",
            )
        if team_golfer.role == TeamRole.CAPTAIN:
            if team_has_captain:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT,
                    detail=f"Team '{team_data.name}' cannot have more than one captain",
                )
            team_has_captain = True
    if not team_has_captain:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Team '{team_data.name}' must have a captain",
        )


def get_golfer_ids_for_flight(
    *, session: Session, flight_id: int, exclude_team_id: Optional[int] = None
) -> List[int]:
    if exclude_team_id is None:
        return session.exec(
            select(Golfer.id)
            .join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id)
            .join(
                FlightTeamLink,
                onclause=FlightTeamLink.team_id == TeamGolferLink.team_id,
            )
            .where(FlightTeamLink.flight_id == flight_id)
        ).all()
    else:
        return session.exec(
            select(Golfer.id)
            .join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id)
            .join(
                FlightTeamLink,
                onclause=FlightTeamLink.team_id == TeamGolferLink.team_id,
            )
            .where(FlightTeamLink.flight_id == flight_id)
            .where(TeamGolferLink.team_id != exclude_team_id)
        ).all()


def get_golfer_ids_for_tournament(
    *, session: Session, tournament_id: int, exclude_team_id: Optional[int] = None
) -> List[int]:
    if exclude_team_id is None:
        return session.exec(
            select(Golfer.id)
            .join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id)
            .join(
                TournamentTeamLink,
                onclause=TournamentTeamLink.team_id == TeamGolferLink.team_id,
            )
            .where(TournamentTeamLink.tournament_id == tournament_id)
        ).all()
    else:
        return session.exec(
            select(Golfer.id)
            .join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id)
            .join(
                TournamentTeamLink,
                onclause=TournamentTeamLink.team_id == TeamGolferLink.team_id,
            )
            .where(TournamentTeamLink.tournament_id == tournament_id)
            .where(TeamGolferLink.team_id != exclude_team_id)
        ).all()


def add_golfer_to_team_for_flight(
    *, session: Session, team_golfer: TeamGolferSignupData, team_id: int, flight_id: int
) -> None:
    # Add team-golfer link
    team_golfer_link_db = TeamGolferLink(
        team_id=team_id,
        golfer_id=team_golfer.golfer_id,
        division_id=team_golfer.division_id,
        role=team_golfer.role,
    )
    session.add(team_golfer_link_db)
    session.commit()

    # Add registrations/payment (as needed)
    flight_db = session.exec(select(Flight).where(Flight.id == flight_id)).one()
    flight_dues_amount = session.exec(
        select(LeagueDues.amount)
        .where(LeagueDues.year == flight_db.year)
        .where(LeagueDues.type == LeagueDuesType.FLIGHT_DUES)
    ).one()
    golfer_dues_payment_db = session.exec(
        select(LeagueDuesPayment)
        .where(LeagueDuesPayment.golfer_id == team_golfer.golfer_id)
        .where(LeagueDuesPayment.year == flight_db.year)
        .where(LeagueDuesPayment.type == LeagueDuesType.FLIGHT_DUES)
    ).one_or_none()
    if not golfer_dues_payment_db:
        golfer_dues_payment_db = LeagueDuesPayment(
            golfer_id=team_golfer.golfer_id,
            year=flight_db.year,
            type=LeagueDuesType.FLIGHT_DUES,
            amount_due=flight_dues_amount,
        )
        session.add(golfer_dues_payment_db)
        session.commit()


def create_team_for_flight(*, session: Session, team_data: TeamSignupData) -> TeamRead:
    # Add team to database
    team_db = Team(name=team_data.name)
    session.add(team_db)
    session.commit()

    # Add flight-team link
    flight_team_link_db = FlightTeamLink(
        flight_id=team_data.flight_id, team_id=team_db.id
    )
    session.add(flight_team_link_db)
    session.commit()

    # Add golfers to team
    for team_golfer in team_data.golfer_data:
        add_golfer_to_team_for_flight(
            session=session,
            team_golfer=team_golfer,
            team_id=team_db.id,
            flight_id=team_data.flight_id,
        )

    # Return new team
    return team_db


def update_team_for_flight(
    *, session: Session, team_data: TeamSignupData, team_db: Team
) -> TeamRead:
    # Update/remove existing golfers on team
    existing_golfer_ids = copy.deepcopy([golfer.id for golfer in team_db.golfers])
    updated_golfer_ids = [golfer.golfer_id for golfer in team_data.golfer_data]
    for existing_golfer in team_db.golfers:
        team_golfer_link_db = session.exec(
            select(TeamGolferLink)
            .where(TeamGolferLink.team_id == team_db.id)
            .where(TeamGolferLink.golfer_id == existing_golfer.id)
        ).one_or_none()
        if not team_golfer_link_db:
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f"Unable to find link for golfer '{existing_golfer.name}' to team '{team_db.name}' (id={team_db.id})",
            )
        if existing_golfer.id not in updated_golfer_ids:  # remove
            print(
                f"Deleting team-golfer link: golfer_id={team_golfer_link_db.golfer_id}, team_id={team_golfer_link_db.team_id}"
            )
            session.delete(team_golfer_link_db)
        else:  # update
            for golfer_data in team_data.golfer_data:
                if golfer_data.golfer_id == existing_golfer.id:
                    setattr(team_golfer_link_db, "division_id", golfer_data.division_id)
                    setattr(team_golfer_link_db, "role", golfer_data.role)
                    session.add(team_golfer_link_db)
                    session.commit()

    # Add new golfers on team
    for golfer_data in team_data.golfer_data:
        if golfer_data.golfer_id not in existing_golfer_ids:
            add_golfer_to_team_for_flight(
                session=session,
                team_golfer=golfer_data,
                team_id=team_db.id,
                flight_id=team_data.flight_id,
            )

    # Update team name
    setattr(team_db, "name", team_data.name)
    session.add(team_db)
    session.commit()

    # Return updated team
    session.refresh(team_db)
    return team_db


def create_team_for_tournament(
    *,
    session: Session = Depends(get_sql_db_session),
    team_data: TeamSignupData,
) -> TeamRead:
    # Validate golfers in signup
    validate_team_signup_data(session=session, team_data=team_data)

    # Add team to database
    team_db = Team(name=team_data.name)
    session.add(team_db)
    session.commit()

    # Add tournament-team link
    tournament_team_link_db = TournamentTeamLink(
        tournament_id=team_data.tournament_id, team_id=team_db.id
    )
    session.add(tournament_team_link_db)
    session.commit()

    # Add team-golfer links
    for team_golfer in team_data.golfer_data:
        team_golfer_link_db = TeamGolferLink(
            team_id=team_db.id,
            golfer_id=team_golfer.golfer_id,
            division_id=team_golfer.division_id,
            role=team_golfer.role,
        )
        session.add(team_golfer_link_db)
        session.commit()

    # Add golfer registrations/payments (as needed)
    tournament_db = session.exec(
        select(Tournament).where(Tournament.id == team_data.tournament_id)
    ).one()
    for team_golfer in team_data.golfer_data:
        golfer_dues_payment_db = session.exec(
            select(LeagueDuesPayment)
            .where(LeagueDuesPayment.golfer_id == team_golfer.golfer_id)
            .where(LeagueDuesPayment.year == tournament_db.year)
        ).one_or_none()
        if (
            not golfer_dues_payment_db
        ):  # no dues payment found for golfer, pay non-member fee
            golfer_dues_payment_db = TournamentEntryFeePayment(
                golfer_id=team_golfer.golfer_id,
                year=tournament_db.year,
                tournament_id=tournament_db.id,
                type=TournamentEntryFeeType.NON_MEMBER_FEE,
                amount_due=tournament_db.non_members_entry_fee,
            )
        else:  # dues payment found for golfer, pay member fee
            golfer_dues_payment_db = TournamentEntryFeePayment(
                golfer_id=team_golfer.golfer_id,
                year=tournament_db.year,
                tournament_id=tournament_db.id,
                type=TournamentEntryFeeType.MEMBER_FEE,
                amount_due=tournament_db.members_entry_fee,
            )
        session.add(golfer_dues_payment_db)
        session.commit()

    # Return new team
    return team_db


def update_team_for_tournament(
    *, session: Session, team_data: TeamSignupData, team_db: Team
) -> TeamRead:
    raise HTTPException(
        status_code=HTTPStatus.NOT_IMPLEMENTED, detail="Team update not yet implemented"
    )
