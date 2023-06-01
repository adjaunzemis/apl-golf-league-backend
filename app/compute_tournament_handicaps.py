import os
import csv
from functools import lru_cache
from typing import List, Optional
from datetime import datetime, timedelta
from datetime import date as dt_date
from sqlmodel import SQLModel, Session, select, create_engine, desc
from pydantic import BaseSettings

from models.course import Course
from models.track import Track
from models.tee import Tee, TeeGender
from models.hole import Hole
from models.golfer import Golfer, GolferAffiliation
from models.flight import Flight
from models.division import Division
from models.flight_division_link import FlightDivisionLink
from models.team import Team
from models.team_golfer_link import TeamGolferLink, TeamRole
from models.flight_team_link import FlightTeamLink
from models.match import Match
from models.round import Round, RoundSummary, ScoringType, RoundType
from models.round_golfer_link import RoundGolferLink
from models.hole_result import HoleResult, HoleResultData
from models.match_round_link import MatchRoundLink
from models.tournament import Tournament
from models.tournament_division_link import TournamentDivisionLink
from models.tournament_team_link import TournamentTeamLink
from models.tournament_round_link import TournamentRoundLink
from models.officer import Officer
from models.payment import (
    LeagueDues,
    LeagueDuesType,
    LeagueDuesPayment,
    TournamentEntryFeeType,
    TournamentEntryFeePayment,
    PaymentMethod,
)
from models.qualifying_score import QualifyingScore
from models.user import User
from utilities.apl_handicap_system import APLHandicapSystem
from utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem


class Settings(BaseSettings):
    apl_golf_league_api_url: str
    apl_golf_league_api_database_connector: str
    apl_golf_league_api_database_user: str
    apl_golf_league_api_database_password: str
    apl_golf_league_api_database_url: str
    apl_golf_league_api_database_port_external: int
    apl_golf_league_api_database_port_internal: int
    apl_golf_league_api_database_name: str
    apl_golf_league_api_database_echo: bool = True
    apl_golf_league_api_access_token_secret_key: str
    apl_golf_league_api_access_token_algorithm: str
    apl_golf_league_api_access_token_expire_minutes: int = 120
    mail_username: str
    mail_password: str
    mail_from_address: str
    mail_from_name: str
    mail_server: str
    mail_port: int

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


class HandicapIndexData(SQLModel):
    active_date: str
    active_handicap_index: float = None
    active_rounds: Optional[List[RoundSummary]] = None
    pending_handicap_index: Optional[float] = None
    pending_rounds: Optional[List[RoundSummary]] = None


if __name__ == "__main__":
    # TODO: Make this a runnable task

    # TOURNAMENT_ID = 24  # Musket Ridge (2023) TODO: un-hardcode id
    TOURNAMENT_ID = 27  # Worthington Manor (2023) TODO: un-hardcode id

    ahs = APLHandicapSystem()

    settings = get_settings()

    DB_URL = "http://localhost"  # TODO: replace with external database url!
    DB_PORT = (
        settings.apl_golf_league_api_database_port_external
    )  # NOTE: using external port, not running from inside container
    db_uri = f"{settings.apl_golf_league_api_database_connector}://{settings.apl_golf_league_api_database_user}:{settings.apl_golf_league_api_database_password}@{DB_URL}:{DB_PORT}/{settings.apl_golf_league_api_database_name}"

    print(
        f"Computing tournament (id={TOURNAMENT_ID}) handicaps in database: {settings.apl_golf_league_api_database_url}"
    )
    engine = create_engine(db_uri, echo=False)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:

        # Get tournament and course info
        tournament_db = session.exec(
            select(Tournament).where(Tournament.id == TOURNAMENT_ID)
        ).one()
        course_db = session.exec(
            select(Course).where(Course.id == tournament_db.course_id)
        ).one()

        # Get divisions and associated tees for this tournament
        divisions_list = session.exec(
            select(Division)
            .join(
                TournamentDivisionLink,
                onclause=TournamentDivisionLink.division_id == Division.id,
            )
            .where(TournamentDivisionLink.tournament_id == TOURNAMENT_ID)
        ).all()
        division_tees = {}
        for division_db in divisions_list:
            division_tees[division_db.id] = {
                "primary": session.exec(
                    select(Tee)
                    .join(Division, onclause=Division.primary_tee_id == Tee.id)
                    .where(Division.id == division_db.id)
                ).one(),
                "secondary": session.exec(
                    select(Tee)
                    .join(Division, onclause=Division.secondary_tee_id == Tee.id)
                    .where(Division.id == division_db.id)
                ).one(),
            }

        # Get golfers signed up for this tournament
        golfer_team_list = session.exec(
            select(Golfer, Team, TeamGolferLink)
            .join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id)
            .join(
                TournamentTeamLink,
                onclause=TournamentTeamLink.team_id == TeamGolferLink.team_id,
            )
            .join(Team, onclause=Team.id == TournamentTeamLink.team_id)
            .where(TournamentTeamLink.tournament_id == TOURNAMENT_ID)
        ).all()

        # For each golfer:
        HEADERS = [
            "Team",
            "Golfer",
            "Division",
            "Handicap Index",
            "Front Tee",
            "Front Par",
            "Front Rating",
            "Front Slope",
            "Front CH",
            "Back Tee",
            "Back Par",
            "Back Rating",
            "Back Slope",
            "Back CH",
            "Tournament CH",
        ]
        DATA = []
        for golfer_db, team_db, team_golfer_link_db in golfer_team_list:
            # TODO: Fix handicap validity date, get relevant handicap index
            # NOTE: This will be much easier when historical handicap table is available

            # Compute course handicaps
            if golfer_db.handicap_index is None:
                course_handicap_primary = 0
                course_handicap_secondary = 0
            else:
                tee_primary = division_tees[team_golfer_link_db.division_id]["primary"]
                course_handicap_primary = ahs.compute_course_handicap(
                    par=tee_primary.par,
                    rating=tee_primary.rating,
                    slope=tee_primary.slope,
                    handicap_index=golfer_db.handicap_index,
                )

                tee_secondary = division_tees[team_golfer_link_db.division_id][
                    "secondary"
                ]
                course_handicap_secondary = ahs.compute_course_handicap(
                    par=tee_secondary.par,
                    rating=tee_secondary.rating,
                    slope=tee_secondary.slope,
                    handicap_index=golfer_db.handicap_index,
                )

            course_handicap = round(course_handicap_primary + course_handicap_secondary)

            DATA.append(
                [
                    team_db.name,
                    golfer_db.name,
                    golfer_db.handicap_index,
                    division_db.name,
                    tee_primary.name,
                    tee_primary.par,
                    tee_primary.rating,
                    tee_primary.slope,
                    round(course_handicap_primary, 2),
                    tee_secondary.name,
                    tee_secondary.par,
                    tee_secondary.rating,
                    tee_secondary.slope,
                    round(course_handicap_secondary, 2),
                    course_handicap,
                ]
            )

            print(
                f"{team_db.name}: {golfer_db.name} ({golfer_db.handicap_index}), Front: {tee_primary.name} ({tee_primary.rating}/{tee_primary.slope}) -> {course_handicap_primary:0.2f}, Back: {tee_secondary.name} ({tee_secondary.rating}/{tee_secondary.slope}) -> {course_handicap_secondary:0.2f} | Course Handicap = {course_handicap}"
            )

        # Output to spreadsheet
        filename = f"handicaps_{tournament_db.name.lower().replace(' ', '')}_{tournament_db.year}.csv"
        print(f"Writing results to file: {filename}")

        with open(filename, "w", newline="") as file:
            csvwriter = csv.writer(file)

            csvwriter.writerow(
                ["Tournament:", f"{tournament_db.name} ({tournament_db.year})"]
            )
            csvwriter.writerow(
                ["Date:", f"{tournament_db.date.replace(tzinfo=None).isoformat()}"]
            )
            csvwriter.writerow(["Course:", f"{course_db.name} ({course_db.year})"])

            csvwriter.writerow([])

            csvwriter.writerow(HEADERS)
            csvwriter.writerows(DATA)

        print("Done!")
