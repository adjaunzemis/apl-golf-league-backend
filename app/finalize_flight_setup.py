"""
Finalized flight setup after team sign-ups

"""

from functools import lru_cache
from sqlmodel import SQLModel, Session, create_engine, select
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
from models.round import Round
from models.round_golfer_link import RoundGolferLink
from models.hole_result import HoleResult
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
from models.user import User


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


def add_scheduled_matches(
    *, session: Session, flight_db: Flight, dry_run: bool = False
):
    flight_team_links_db = session.exec(
        select(FlightTeamLink).where(FlightTeamLink.flight_id == flight_db.id)
    ).all()
    if (not flight_team_links_db) or (len(flight_team_links_db) == 0):
        raise ValueError(
            "Unable to find teams in flight: "
            + flight_db.name
            + " ("
            + flight_db.year
            + ")"
        )

    team_ids = [link.team_id for link in flight_team_links_db]

    # TODO: Implement other team-number/week-number schedules as needed
    if (flight_db.weeks == 18) and (len(team_ids) == 5):
        matchup_matrix = [  # 5 teams, 18 weeks
            [4, 3, 2, 1, None],  # week 1
            [2, 1, 5, None, 3],  # week 2
            [5, 4, None, 2, 1],  # week 3
            [3, None, 1, 5, 4],  # week 4
            [None, 5, 4, 3, 2],  # week 5
            [4, 3, 2, 1, 4],  # week 6 (extra: 5 vs 4)
            [2, 1, 5, None, 3],  # week 7
            [5, 4, 1, 2, 1],  # week 8 (extra: 3 vs 1)
            [3, None, 1, 5, 4],  # week 9
            [None, 5, 4, 3, 2],  # week 10
            [4, 3, 2, 1, None],  # week 11
            [2, 1, 5, 3, 3],  # week 12 (extra: 4 vs 3)
            [5, 4, None, 2, 1],  # week 13
            [3, 5, 1, 5, 4],  # week 14 (extra: 2 vs 5)
            [None, 5, 4, 3, 2],  # week 15
            [4, 3, 2, 1, None],  # week 16
            [2, 1, 5, None, 3],  # week 17
            [5, 4, None, 2, 1],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 6):
        matchup_matrix = [  # 6 teams, 18 weeks
            [6, 5, 4, 3, 2, 1],  # week 1
            [5, 4, 6, 2, 1, 3],  # week 2
            [4, 3, 2, 1, 6, 5],  # week 3
            [3, 6, 1, 5, 4, 2],  # week 4
            [2, 1, 5, 6, 3, 4],  # week 5
            [6, 5, 4, 3, 2, 1],  # week 6
            [None, None, None, None, None, None],  # week 7
            [5, 4, 6, 2, 1, 3],  # week 8
            [4, 3, 2, 1, 6, 5],  # week 9
            [3, 6, 1, 5, 4, 2],  # week 10
            [2, 1, 5, 6, 3, 4],  # week 11
            [None, None, None, None, None, None],  # week 12
            [6, 5, 4, 3, 2, 1],  # week 13
            [5, 4, 6, 2, 1, 3],  # week 14
            [4, 3, 2, 1, 6, 5],  # week 15
            [3, 6, 1, 5, 4, 2],  # week 16
            [2, 1, 5, 6, 3, 4],  # week 17
            [6, 5, 4, 3, 2, 1],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 7):
        matchup_matrix = [  # 7 teams, 18 weeks
            [6, 5, 4, 3, 2, 1, None],  # week 1
            [5, 4, 7, 2, 1, None, 3],  # week 2
            [4, 3, 2, 1, None, 7, 6],  # week 3
            [3, 7, 1, None, 6, 5, 2],  # week 4
            [2, 1, None, 6, 7, 4, 5],  # week 5
            [7, None, 6, 5, 4, 3, 1],  # week 6
            [None, 6, 5, 7, 3, 2, 4],  # week 7
            [6, 5, 4, 3, 2, 1, 5],  # week 8
            [5, 4, 7, 2, 1, 4, 3],  # week 9
            [4, 3, 2, 1, 7, 7, 6],  # week 10
            [3, 7, 1, 6, 6, 5, 2],  # week 11
            [2, 1, None, 6, 7, 4, 5],  # week 12
            [7, None, 6, 5, 4, 3, 1],  # week 13
            [None, 6, 5, 7, 3, 2, 4],  # week 14
            [6, 5, 4, 3, 2, 1, None],  # week 15
            [5, 4, 7, 2, 1, None, 3],  # week 16
            [4, 3, 2, 1, None, 7, 6],  # week 17
            [3, 7, 1, None, 6, 5, 2],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 8):
        matchup_matrix = [  # 8 teams, 18 weeks
            [8, 7, 6, 5, 4, 3, 2, 1],  # week 1
            [7, 6, 5, 8, 3, 2, 1, 4],  # week 2
            [6, 5, 4, 3, 2, 1, 8, 7],  # week 3
            [5, 4, 8, 2, 1, 7, 6, 3],  # week 4
            [4, 3, 2, 1, 7, 8, 5, 6],  # week 5
            [3, 8, 1, 7, 6, 5, 4, 2],  # week 6
            [None, None, None, None, None, None, None, None],  # week 7
            [2, 1, 7, 6, 8, 4, 3, 5],  # week 8
            [8, 7, 6, 5, 4, 3, 2, 1],  # week 9
            [7, 6, 5, 8, 3, 2, 1, 4],  # week 10
            [6, 5, 4, 3, 2, 1, 8, 7],  # week 11
            [None, None, None, None, None, None, None, None],  # week 12
            [5, 4, 8, 2, 1, 7, 6, 3],  # week 13
            [4, 3, 2, 1, 7, 8, 5, 6],  # week 14
            [3, 8, 1, 7, 6, 5, 4, 2],  # week 15
            [2, 1, 7, 6, 8, 4, 3, 5],  # week 16
            [8, 7, 6, 5, 4, 3, 2, 1],  # week 17
            [7, 6, 5, 8, 3, 2, 1, 4],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 9):
        matchup_matrix = [  # 9 teams, 18 weeks
            [None, 9, 8, 7, 6, 5, 4, 3, 2],  # week 1
            [9, None, 7, 6, 8, 4, 3, 5, 1],  # week 2
            [8, 7, None, 5, 4, 9, 2, 1, 6],  # week 3
            [7, 6, 5, None, 3, 2, 1, 9, 8],  # week 4
            [6, 8, 4, 3, None, 1, 9, 2, 7],  # week 5
            [5, 4, 9, 2, 1, None, 8, 7, 3],  # week 6
            [4, 3, 2, 1, 9, 8, None, 6, 5],  # week 7
            [3, 5, 1, 9, 2, 7, 6, None, 4],  # week 8
            [2, 1, 6, 8, 7, 3, 5, 4, None],  # week 9
            [None, 9, 8, 7, 6, 5, 4, 3, 2],  # week 10
            [9, None, 7, 6, 8, 4, 3, 5, 1],  # week 11
            [8, 7, None, 5, 4, 9, 2, 1, 6],  # week 12
            [7, 6, 5, None, 3, 2, 1, 9, 8],  # week 13
            [6, 8, 4, 3, None, 1, 9, 2, 7],  # week 14
            [5, 4, 9, 2, 1, None, 8, 7, 3],  # week 15
            [4, 3, 2, 1, 9, 8, None, 6, 5],  # week 16
            [3, 5, 1, 9, 2, 7, 6, None, 4],  # week 17
            [2, 1, 6, 8, 7, 3, 5, 4, None],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 10):
        matchup_matrix = [  # 10 teams, 18 weeks
            [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],  # week 1
            [9, 8, 7, 6, 10, 4, 3, 2, 1, 5],  # week 2
            [8, 7, 6, 5, 4, 3, 2, 1, 10, 9],  # week 3
            [7, 6, 5, 10, 3, 2, 1, 9, 8, 4],  # week 4
            [6, 5, 4, 3, 2, 1, 9, 10, 7, 8],  # week 5
            [5, 4, 10, 2, 1, 9, 8, 7, 6, 3],  # week 6
            [None, None, None, None, None, None, None, None, None, None],  # week 7
            [4, 3, 2, 1, 9, 8, 10, 6, 5, 7],  # week 8
            [3, 10, 1, 9, 8, 7, 6, 5, 4, 2],  # week 9
            [2, 1, 9, 8, 7, 10, 5, 4, 3, 6],  # week 10
            [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],  # week 11
            [None, None, None, None, None, None, None, None, None, None],  # week 12
            [9, 8, 7, 6, 10, 4, 3, 2, 1, 5],  # week 13
            [8, 7, 6, 5, 4, 3, 2, 1, 10, 9],  # week 14
            [7, 6, 5, 10, 3, 2, 1, 9, 8, 4],  # week 15
            [6, 5, 4, 3, 2, 1, 9, 10, 7, 8],  # week 16
            [5, 4, 10, 2, 1, 9, 8, 7, 6, 3],  # week 17
            [4, 3, 2, 1, 9, 8, 10, 6, 5, 7],  # week 18
        ]
    else:
        raise ValueError(
            f"No pre-defined {flight_db.weeks}-week matchup matrix for {len(team_ids)} teams"
        )

    for week_idx in range(len(matchup_matrix)):
        week = week_idx + 1
        for team_idx in range(len(team_ids)):
            team_id = team_ids[team_idx]
            if matchup_matrix[week_idx][team_idx]:  # check for byes
                opponent_team_id = team_ids[matchup_matrix[week_idx][team_idx] - 1]
                match_db = session.exec(
                    select(Match)
                    .where(Match.flight_id == flight_db.id)
                    .where(Match.week == week)
                    .where(
                        (
                            (Match.home_team_id == team_id)
                            & (Match.away_team_id == opponent_team_id)
                        )
                        | (Match.home_team_id == opponent_team_id)
                        & (Match.away_team_id == team_id)
                    )
                ).one_or_none()
                if not match_db:
                    print(
                        f"Adding match: week={week}, home_team_id={team_id}, away_team_id={opponent_team_id}"
                    )
                    if not dry_run:
                        match_db = Match(
                            flight_id=flight_db.id,
                            week=week,
                            home_team_id=team_id,
                            away_team_id=opponent_team_id,
                        )
                        session.add(match_db)
                        session.commit()


if __name__ == "__main__":
    YEAR = 2023
    DRY_RUN = False

    settings = get_settings()

    DB_URL = "localhost"  # TODO: replace with external database url!
    DB_PORT = (
        settings.apl_golf_league_api_database_port_external
    )  # NOTE: using external port, not running from inside container
    db_uri = f"{settings.apl_golf_league_api_database_connector}://{settings.apl_golf_league_api_database_user}:{settings.apl_golf_league_api_database_password}@{DB_URL}:{DB_PORT}/{settings.apl_golf_league_api_database_name}"

    print(
        f"Finalizing flight setup in database: {settings.apl_golf_league_api_database_url}"
    )
    engine = create_engine(db_uri, echo=False)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # For each flight:
        flights_db = session.exec(select(Flight).where(Flight.year == YEAR)).all()
        for flight_db in flights_db:
            print(f"Flight: {flight_db.name} ({flight_db.year})")
            # Initialize schedule with matches
            try:
                add_scheduled_matches(
                    session=session, flight_db=flight_db, dry_run=DRY_RUN
                )
            except Exception as e:
                print(f"ERROR: Unable to add scheduled matches - {e}")

    print("Done!")
