import csv
from typing import List, Optional
from sqlmodel import SQLModel, select

from app.dependencies import get_sql_db_session
from app.models.course import Course
from app.models.tee import Tee
from app.models.golfer import Golfer
from app.models.division import Division
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink
from app.models.round import RoundSummary
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


if __name__ == "__main__":
    # TODO: Make this a runnable task

    # TOURNAMENT_ID = 24  # Musket Ridge (2023) TODO: un-hardcode id
    TOURNAMENT_ID = 27  # Worthington Manor (2023) TODO: un-hardcode id

    print(f"Computing tournament (id={TOURNAMENT_ID}) handicaps")

    ahs = APLHandicapSystem()
    with get_sql_db_session as session:

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
