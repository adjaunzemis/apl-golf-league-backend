import csv
from typing import List, Optional

from sqlmodel import Session, SQLModel, create_engine, select

from app.dependencies import get_settings
from app.models.course import Course
from app.models.division import Division
from app.models.golfer import Golfer
from app.models.round import RoundSummary
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink
from app.models.tee import Tee
from app.models.tournament import Tournament
from app.models.tournament_division_link import TournamentDivisionLink
from app.models.tournament_team_link import TournamentTeamLink
from app.utilities.apl_handicap_system import APLHandicapSystem


class HandicapIndexData(SQLModel):
    active_date: str
    active_handicap_index: float = None
    active_rounds: Optional[List[RoundSummary]] = None
    pending_handicap_index: Optional[float] = None
    pending_rounds: Optional[List[RoundSummary]] = None


def organize_team_handicaps_scramble(
    hcps: list[float],
) -> tuple[float, float, float, float]:
    sorted_indexes = sorted(hcps)
    if len(hcps) == 4:
        return tuple(sorted_indexes)
    elif len(hcps) == 3:
        return (
            sorted_indexes[0],
            sorted_indexes[1],
            sorted_indexes[1],
            sorted_indexes[2],
        )
    elif len(hcps) == 2:
        return (
            sorted_indexes[0],
            sorted_indexes[0],
            sorted_indexes[1],
            sorted_indexes[1],
        )
    raise ValueError(
        f"Unable to organize team handicap indexes given {len(hcps)} indexes"
    )


def compute_team_handicap_scramble(
    hcp_a: int, hcp_b: int, hcp_c: int, hcp_d: int
) -> int:
    return round(0.25 * hcp_a + 0.20 * hcp_b + 0.15 * hcp_c + 0.10 * hcp_d)


if __name__ == "__main__":
    # TODO: Make this a runnable task

    # TOURNAMENT_ID = 24  # Musket Ridge (2023) TODO: un-hardcode id
    # TOURNAMENT_ID = 27  # Worthington Manor (2023) TODO: un-hardcode id
    # TOURNAMENT_ID = 31  # Lake Presidential (2023) TODO: un-hardcode id
    # TOURNAMENT_ID = 29  # Maryland National (2023) TODO: un-hardcode id
    # TOURNAMENT_ID = 32  # Musket Ridge (2024) TODO: un-hardcode id
    # TOURNAMENT_ID = 33  # Lake Presidential (2024) TODO: un-hardcode id
    # TOURNAMENT_ID = 34  # Eagle's Nest (2024) TODO: un-hardcode id
    TOURNAMENT_ID = 35  # Montgomery CC (2024) TODO: un-hardcode id

    print(f"Computing tournament (id={TOURNAMENT_ID}) handicaps")

    ahs = APLHandicapSystem()

    settings = get_settings()

    DB_URL = settings.apl_golf_league_api_url
    DB_PORT = (
        settings.apl_golf_league_api_database_port_external
    )  # NOTE: using external port, not running from inside container
    db_uri = f"{settings.apl_golf_league_api_database_connector}://{settings.apl_golf_league_api_database_user}:{settings.apl_golf_league_api_database_password}@{DB_URL}:{DB_PORT}/{settings.apl_golf_league_api_database_name}"

    print(
        f"Computing tournament (id={TOURNAMENT_ID}) handicaps in database: {settings.apl_golf_league_api_database_url}"
    )
    engine = create_engine(db_uri, echo=False)

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
            select(Golfer, Team, Division)
            .join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id)
            .join(Division, onclause=Division.id == TeamGolferLink.division_id)
            .join(
                TournamentTeamLink,
                onclause=TournamentTeamLink.team_id == TeamGolferLink.team_id,
            )
            .join(Team, onclause=Team.id == TournamentTeamLink.team_id)
            .where(TournamentTeamLink.tournament_id == TOURNAMENT_ID)
        ).all()

        # For each golfer:
        GOLFER_HEADERS = [
            "Team",
            "Golfer",
            "Handicap Index",
            "Division",
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
        GOLFER_DATA = []
        for golfer_db, team_db, division_db in golfer_team_list:
            # TODO: Fix handicap validity date, get relevant handicap index
            # NOTE: This will be much easier when historical handicap table is available

            # Compute course handicaps
            if golfer_db.handicap_index is None:
                course_handicap_primary = 0
                course_handicap_secondary = 0
            else:
                tee_primary = division_tees[division_db.id]["primary"]
                course_handicap_primary = ahs.compute_course_handicap(
                    par=tee_primary.par,
                    rating=tee_primary.rating,
                    slope=tee_primary.slope,
                    handicap_index=golfer_db.handicap_index,
                )

                tee_secondary = division_tees[division_db.id]["secondary"]
                course_handicap_secondary = ahs.compute_course_handicap(
                    par=tee_secondary.par,
                    rating=tee_secondary.rating,
                    slope=tee_secondary.slope,
                    handicap_index=golfer_db.handicap_index,
                )

            course_handicap = round(course_handicap_primary + course_handicap_secondary)

            GOLFER_DATA.append(
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

        # Compute team handicaps
        TEAM_DATA = None
        if tournament_db.scramble:
            print(f"Team handicaps (scramble)")

            TEAM_HEADERS = ["Team", "CH A", "CH B", "CH C", "CH D", "Team CH"]
            TEAM_DATA = []

            team_names: list[str] = []
            for golfer_db, team_db, division_db in golfer_team_list:
                if team_db.name not in team_names:
                    team_names.append(team_db.name)

                    # TODO: Make less fragile in case column numbers change
                    team_hcps = [
                        golfer_data[14]
                        for golfer_data in GOLFER_DATA
                        if golfer_data[0] == team_db.name
                    ]
                    hcp_a, hcp_b, hcp_c, hcp_d = organize_team_handicaps_scramble(
                        team_hcps
                    )
                    team_hcp = compute_team_handicap_scramble(
                        hcp_a, hcp_b, hcp_c, hcp_d
                    )

                    TEAM_DATA.append(
                        [team_db.name, hcp_a, hcp_b, hcp_c, hcp_d, team_hcp]
                    )

                    print(
                        f"{team_db.name}: [{hcp_a}, {hcp_b}, {hcp_c}, {hcp_d}] -> {team_hcp}"
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

            csvwriter.writerow(GOLFER_HEADERS)
            csvwriter.writerows(GOLFER_DATA)

            if TEAM_DATA is not None:
                csvwriter.writerow([])
                csvwriter.writerow(TEAM_HEADERS)
                csvwriter.writerows(TEAM_DATA)

        print("Done!")
