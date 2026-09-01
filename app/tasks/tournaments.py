from datetime import datetime

from loguru import logger
from sqlmodel import Session

from app.database import courses as db_courses
from app.database import tournaments as db_tournaments
from app.models.base import APLGLBaseModel
from app.models.query_helpers import get_handicap_index_data
from app.models.tournament import Tournament
from app.utilities.apl_handicap_system import APLHandicapSystem
from app.utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem


class TournamentGolferHandicapData(APLGLBaseModel):
    team: str
    golfer: str
    handicap_index: float | None
    division: str
    front_tee: str
    front_par: int
    front_rating: float
    front_slope: float
    front_course_handicap: float
    back_tee: str
    back_par: int
    back_rating: float
    back_slope: float
    back_course_handicap: float
    tournament_course_handicap: int


class TournamentTeamHandicapData(APLGLBaseModel):
    team: str
    tournament_team_handicap: int


def get_handicap_system_for_tournament(
    tournament: Tournament,
) -> APLHandicapSystem | APLLegacyHandicapSystem:
    """Gets relevant handicap system for the given tournament."""
    if tournament.year < 2022:
        return APLLegacyHandicapSystem()
    else:
        return APLHandicapSystem()


def compute_team_handicap_scramble(handicaps: list[int]) -> int:
    """Computes team handicap for a scramble event using USGA-recommended weighting."""
    if len(handicaps) < 2 or len(handicaps) > 4:
        err_msg = f"Cannot compute tournament team handicap for team with {len(handicaps)} players"
        logger.error(err_msg)
        raise ValueError(err_msg)

    sorted_handicaps = sorted(handicaps)
    if len(sorted_handicaps) == 2:
        hcp_a, hcp_b, hcp_c, hcp_d = [
            sorted_handicaps[0],
            sorted_handicaps[0],
            sorted_handicaps[1],
            sorted_handicaps[1],
        ]
    elif len(sorted_handicaps) == 3:
        hcp_a, hcp_b, hcp_c, hcp_d = [
            sorted_handicaps[0],
            sorted_handicaps[1],
            sorted_handicaps[1],
            sorted_handicaps[2],
        ]
    else:
        hcp_a, hcp_b, hcp_c, hcp_d = [
            sorted_handicaps[0],
            sorted_handicaps[1],
            sorted_handicaps[2],
            sorted_handicaps[3],
        ]

    return round(0.25 * hcp_a + 0.20 * hcp_b + 0.15 * hcp_c + 0.10 * hcp_d)


def compile_tournament_handicaps(
    *, session: Session, tournament_id: int
) -> tuple[list[TournamentGolferHandicapData], list[TournamentTeamHandicapData]]:
    tournament = db_tournaments.get_by_id(session, tournament_id)
    if tournament is None:
        err_msg = f"Cannot find tournament with id {tournament_id}"
        logger.error(err_msg)
        raise ValueError(err_msg)
    logger.info(
        f"Compiling tournament handicap data for '{tournament.name}' ({tournament.year})"
    )

    ahs = get_handicap_system_for_tournament(tournament)
    logger.info(f"Using handicap system: {type(ahs)}")

    handicap_allowance = ahs.get_handicap_allowance(
        is_shamble=(not (tournament.shamble is None) and tournament.shamble)
    )
    logger.info(f"Handicap allowance: {handicap_allowance}")

    course = db_courses.get_courses_by_id(
        session=session, course_ids=[tournament.course_id]
    )
    if len(course) != 1:
        err_msg = f"Cannot find tournament course by id {tournament.course_id}"
        logger.error(err_msg)
        raise ValueError(err_msg)
    course = course[0]
    logger.info(f"Tournament course: '{course.name}' ({course.year})")

    divisions = db_tournaments.get_divisions(
        session=session, tournament_id=tournament_id
    )
    logger.info(f"Tournament divisions: {[div.name for div in divisions]}")
    divisions_by_name = {div.name: div for div in divisions}

    teams = db_tournaments.get_teams(session=session, tournament_id=tournament_id)
    if teams is None:
        err_msg = f"Cannot find teams for tournament {tournament.name}"
        logger.error(err_msg)
        raise ValueError(err_msg)
    teams_by_id = {team.team_id: team for team in teams}
    logger.info(f"Processing handicaps for {len(teams)} teams")

    if tournament.date is None:
        err_msg = f"Cannot compute handicaps for tournament without date"
        logger.error(err_msg)
        raise ValueError(err_msg)
    hcp_min_date = datetime(tournament.date.year - 2, 1, 1)
    hcp_max_date = tournament.date
    logger.info(
        f"Computing handicap indexes using rounds from {hcp_min_date} to {hcp_max_date}"
    )

    team_golfer_handicaps: dict[int, list[TournamentGolferHandicapData]] = {}
    for team in teams:
        logger.info(f"Team '{team.name}', {len(team.golfers)} golfers")
        team_golfer_handicaps[team.team_id] = []

        for golfer in team.golfers:
            golfer_division = divisions_by_name[golfer.division]

            golfer_hcp_data = get_handicap_index_data(
                session=session,
                golfer_id=golfer.golfer_id,
                min_date=hcp_min_date,
                max_date=hcp_max_date,
            )
            golfer_hcp_index = golfer_hcp_data.active_handicap_index
            if golfer_hcp_index is None:
                ch_front = 0
                ch_back = 0
            else:
                ch_front = ahs.compute_course_handicap(
                    par=golfer_division.primary_tee_par,
                    rating=golfer_division.primary_tee_rating,
                    slope=golfer_division.primary_tee_slope,
                    handicap_index=golfer_hcp_index,
                )
                ch_back = ahs.compute_course_handicap(
                    par=golfer_division.secondary_tee_par,
                    rating=golfer_division.secondary_tee_rating,
                    slope=golfer_division.secondary_tee_slope,
                    handicap_index=golfer_hcp_index,
                )
            ch_tournament = round(handicap_allowance * (ch_front + ch_back))

            data = TournamentGolferHandicapData(
                team=team.name,
                golfer=golfer.name,
                handicap_index=golfer_hcp_index,
                division=golfer.division,
                front_tee=golfer_division.primary_tee_name,
                front_par=golfer_division.primary_tee_par,
                front_rating=golfer_division.primary_tee_rating,
                front_slope=golfer_division.primary_tee_slope,
                front_course_handicap=round(ch_front, 2),
                back_tee=golfer_division.secondary_tee_name,
                back_par=golfer_division.secondary_tee_par,
                back_rating=golfer_division.secondary_tee_rating,
                back_slope=golfer_division.secondary_tee_slope,
                back_course_handicap=round(ch_back, 2),
                tournament_course_handicap=ch_tournament,
            )
            logger.info(
                f"{data.team}: {data.golfer} ({data.handicap_index}). Division: {data.division}, ",
                f"Front: {data.front_tee} ({data.front_rating}/{data.front_slope}) -> {ch_front:0.2f}, ",
                f"Back: {data.back_tee} ({data.back_rating}/{data.back_slope}) -> {ch_back:0.2f} | ",
                f"Course Handicap = {ch_tournament}",
            )
            team_golfer_handicaps[team.team_id].append(data)

    all_golfer_handicaps: list[TournamentGolferHandicapData] = []
    for golfer_handicaps in team_golfer_handicaps.values():
        all_golfer_handicaps.extend(golfer_handicaps)

    team_handicaps: list[TournamentTeamHandicapData] = []
    if tournament.scramble:
        logger.info(f"Computing team handicaps for scramble")
        for team_id, golfer_handicaps in team_golfer_handicaps.items():
            team = teams_by_id[team_id]
            team_hcp = TournamentTeamHandicapData(
                team=team.name,
                tournament_team_handicap=compute_team_handicap_scramble(
                    [golfer.tournament_course_handicap for golfer in golfer_handicaps]
                ),
            )

            logger.info(
                f"{team.name}: {[golfer.tournament_course_handicap for golfer in golfer_handicaps]} -> ",
                f"{team_hcp.tournament_team_handicap}",
            )
            team_handicaps.append(team_hcp)

    return (all_golfer_handicaps, team_handicaps)
