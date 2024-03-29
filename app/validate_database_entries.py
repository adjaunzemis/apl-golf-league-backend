"""
Validate entries in database, check for missing links or inconsistencies

"""

import os

from dotenv import load_dotenv
from models.division import Division
from models.flight import Flight
from models.flight_division_link import FlightDivisionLink
from models.flight_team_link import FlightTeamLink
from models.golfer import Golfer
from models.payment import (
    LeagueDuesPayment,
    LeagueDuesType,
    PaymentMethod,
)
from models.team import Team
from models.team_golfer_link import TeamGolferLink
from sqlmodel import Session, SQLModel, create_engine, select


def check_flight_dues_payment_entry(
    *,
    session: Session,
    flight_db: Flight,
    golfer_db: Golfer,
    check_status: bool = False,
):
    payment_db = session.exec(
        select(LeagueDuesPayment)
        .where(LeagueDuesPayment.golfer_id == golfer_db.id)
        .where(LeagueDuesPayment.type == LeagueDuesType.FLIGHT_DUES)
        .where(LeagueDuesPayment.year == flight_db.year)
    ).one_or_none()
    if not payment_db:
        print(f"Missing flight dues payment entry for golfer '{golfer_db.name}'")
        print(
            f"\tINSERT INTO leagueduespayment (golfer_id, year, type, amount_due, amount_paid, is_paid) VALUES ({golfer_db.id}, {flight_db.year}, 'Flight Dues', 40, 0, 0);"
        )
        return
    if check_status:
        if not (
            (payment_db.amount_due <= payment_db.amount_paid)
            or (payment_db.method == PaymentMethod.EXEMPT)
            or (payment_db.method == PaymentMethod.LINKED)
        ):
            print(f"Flight dues payment owed for golfer '{golfer_db.name}'")


def check_division_assignment(
    *, session: Session, flight_db: Flight, team_db: Team, golfer_db: Golfer
):
    division_db = session.exec(
        select(Division)
        .join(TeamGolferLink, onclause=TeamGolferLink.division_id == Division.id)
        .where(TeamGolferLink.team_id == team_db.id)
        .where(TeamGolferLink.golfer_id == golfer_db.id)
    ).one_or_none()
    if not division_db:
        print(
            f"Missing division assignment for golfer '{golfer_db.name}' (id={golfer_db.id}) on team '{team_db.name}' (id={team_db.id})"
        )
        return
    flight_division_links_db = session.exec(
        select(FlightDivisionLink).where(
            FlightDivisionLink.division_id == division_db.id
        )
    ).one_or_none()
    if not flight_division_links_db:
        print(
            f"Invalid division assignment for golfer '{golfer_db.name}' (id={golfer_db.id}) on team '{team_db.name}' (id={team_db.id}), division '{division_db.name}' (id={division_db.id}) not linked to any flights"
        )
    if flight_division_links_db.flight_id != flight_db.id:
        print(
            f"Invalid division assignment for golfer '{golfer_db.name}' (id={golfer_db.id}) on team '{team_db.name}' (id={team_db.id}), division '{division_db.name}' (id={division_db.id}) not linked to flight '{flight_db.name}' (id={flight_db.id})"
        )
        # Find probable division in correct flight
        other_division_db = session.exec(
            select(Division)
            .join(
                FlightDivisionLink,
                onclause=FlightDivisionLink.division_id == Division.id,
            )
            .where(FlightDivisionLink.flight_id == flight_db.id)
            .where(Division.name == division_db.name)
        ).one_or_none()
        if not other_division_db:
            print(f"\tUnable to find probable correct division!")
            return
        print(
            f"\tProbable correct division: '{other_division_db.name}' (id={other_division_db.id})"
        )
        # Print SQL update statement
        print(
            f"\t\tSET division_id = {other_division_db.id} WHERE golfer_id = {golfer_db.id} AND team_id = {team_db.id};"
        )


if __name__ == "__main__":
    YEAR = 2022

    load_dotenv()

    DATABASE_USER = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_USER")
    DATABASE_PASSWORD = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_PASSWORD")
    DATABASE_ADDRESS = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_URL")
    DATABASE_PORT = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_PORT_EXTERNAL")
    DATABASE_NAME = os.environ.get("APL_GOLF_LEAGUE_API_DATABASE_NAME")

    DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_ADDRESS}:{DATABASE_PORT}/{DATABASE_NAME}"

    print(f"Validating database: {DATABASE_NAME}")
    engine = create_engine(DATABASE_URL, echo=False)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # For each flight:
        flights_db = session.exec(select(Flight).where(Flight.year == YEAR)).all()
        for flight_db in flights_db:
            # For each team:
            teams_db = session.exec(
                select(Team)
                .join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id)
                .where(FlightTeamLink.flight_id == flight_db.id)
            ).all()
            for team_db in teams_db:
                # For each golfer:
                golfers_db = session.exec(
                    select(Golfer)
                    .join(
                        TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id
                    )
                    .where(TeamGolferLink.team_id == team_db.id)
                ).all()
                for golfer_db in golfers_db:
                    check_flight_dues_payment_entry(
                        session=session, flight_db=flight_db, golfer_db=golfer_db
                    )
                    check_division_assignment(
                        session=session,
                        flight_db=flight_db,
                        team_db=team_db,
                        golfer_db=golfer_db,
                    )

    print("Done!")
