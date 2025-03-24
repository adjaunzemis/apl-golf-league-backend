import numpy as np
from sqlalchemy.orm import aliased
from sqlmodel import Session, select

from app.models.course import Course
from app.models.division import Division, TournamentDivision
from app.models.golfer import Golfer
from app.models.hole import Hole
from app.models.hole_result import HoleResult
from app.models.match import Match
from app.models.match_round_link import MatchRoundLink
from app.models.query_helpers import get_hole_results_for_rounds, get_tournament_rounds
from app.models.round import Round, RoundResults, RoundSummary
from app.models.round_golfer_link import RoundGolferLink
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink
from app.models.tee import Tee
from app.models.tournament import (
    GolferStatistics,
    Tournament,
    TournamentInfo,
    TournamentStandings,
    TournamentStandingsGolfer,
    TournamentStandingsTeam,
    TournamentStatistics,
    TournamentTeam,
    TournamentTeamGolfer,
)
from app.models.tournament_division_link import TournamentDivisionLink
from app.models.tournament_round_link import TournamentRoundLink
from app.models.tournament_team_link import TournamentTeamLink
from app.models.track import Track
from app.utilities.apl_handicap_system import APLHandicapSystem
from app.utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem


def get_ids(session: Session, year: int | None = None) -> list[int]:
    query = select(Tournament.id)
    if year:
        query = query.where(Tournament.year == year)
    return session.exec(query.order_by(Tournament.id)).all()


def get_info(session: Session, tournament_id: int) -> TournamentInfo:
    tournament = session.exec(
        select(Tournament).where(Tournament.id == tournament_id)
    ).one()
    teams = get_teams(session=session, tournament_id=tournament_id)
    course = session.exec(
        select(Course).where(Course.id == tournament.course_id)
    ).one_or_none()
    return TournamentInfo(
        id=tournament.id,
        year=tournament.year,
        name=tournament.name,
        course=course.name if course is not None else None,
        address=course.address if course is not None else None,
        phone=course.phone if course is not None else None,
        logo_url=tournament.logo_url,
        secretary=tournament.secretary,
        secretary_email=tournament.secretary_email,
        signup_start_date=tournament.signup_start_date.astimezone()
        .replace(microsecond=0)
        .isoformat(),
        signup_stop_date=tournament.signup_stop_date.astimezone()
        .replace(microsecond=0)
        .isoformat(),
        date=tournament.date.astimezone().replace(microsecond=0).isoformat(),
        shotgun=tournament.shotgun,
        strokeplay=tournament.strokeplay,
        bestball=tournament.bestball,
        scramble=tournament.scramble,
        ryder_cup=tournament.ryder_cup,
        individual=tournament.individual,
        chachacha=tournament.chachacha,
        num_teams=len(teams),
    )


def get_divisions(session: Session, tournament_id: int) -> list[TournamentDivision]:
    primary_track = aliased(Track)
    primary_tee = aliased(Tee)
    secondary_track = aliased(Track)
    secondary_tee = aliased(Tee)
    division_query_data = session.exec(
        select(
            Division,
            TournamentDivisionLink,
            primary_tee,
            primary_track,
            secondary_tee,
            secondary_track,
        )
        .join(
            TournamentDivisionLink,
            onclause=TournamentDivisionLink.division_id == Division.id,
        )
        .join(primary_tee, onclause=Division.primary_tee_id == primary_tee.id)
        .join(primary_track, onclause=primary_tee.track_id == primary_track.id)
        .join(secondary_tee, onclause=Division.secondary_tee_id == secondary_tee.id)
        .join(secondary_track, onclause=secondary_tee.track_id == secondary_track.id)
        .where(TournamentDivisionLink.tournament_id == tournament_id)
    )
    return [
        TournamentDivision(
            id=division.id,
            tournament_id=tournament_division_link.tournament_id,
            name=division.name,
            gender=division.gender,
            primary_track_id=primary_track_db.id,
            primary_track_name=primary_track_db.name,
            primary_tee_id=primary_tee_db.id,
            primary_tee_name=primary_tee_db.name,
            primary_tee_par=primary_tee_db.par,
            primary_tee_rating=primary_tee_db.rating,
            primary_tee_slope=primary_tee_db.slope,
            secondary_track_id=secondary_track_db.id,
            secondary_track_name=secondary_track_db.name,
            secondary_tee_id=secondary_tee_db.id,
            secondary_tee_name=secondary_tee_db.name,
            secondary_tee_par=secondary_tee_db.par,
            secondary_tee_rating=secondary_tee_db.rating,
            secondary_tee_slope=secondary_tee_db.slope,
        )
        for division, tournament_division_link, primary_tee_db, primary_track_db, secondary_tee_db, secondary_track_db in division_query_data
    ]


def get_teams(session: Session, tournament_id: int) -> list[TournamentTeam]:
    results = session.exec(
        select(Team, Golfer, TeamGolferLink, Division)
        .join(TournamentTeamLink, onclause=TournamentTeamLink.team_id == Team.id)
        .join(TeamGolferLink, onclause=TeamGolferLink.team_id == Team.id)
        .join(Golfer, onclause=Golfer.id == TeamGolferLink.golfer_id)
        .join(Division, onclause=Division.id == TeamGolferLink.division_id)
        .where(TournamentTeamLink.tournament_id == tournament_id)
    ).all()
    teams: dict[int, TournamentTeam] = {}

    for team, golfer, teamgolferlink, division in results:
        if team.id not in teams:
            teams[team.id] = TournamentTeam(
                tournament_id=tournament_id, team_id=team.id, name=team.name
            )
        teams[team.id].golfers.append(
            TournamentTeamGolfer(
                golfer_id=golfer.id,
                name=golfer.name,
                role=teamgolferlink.role,
                division=division.name,
            )
        )

    for team in teams.values():
        team.golfers.sort(key=lambda g: g.role)

    return list(teams.values())


def get_round_summaries(
    session: Session, tournament_id: int, use_legacy_handicapping: bool = False
) -> list[RoundSummary]:
    round_query_data = session.exec(
        select(Round, RoundGolferLink, Golfer, Course, Track, Tee)
        .join(TournamentRoundLink, onclause=TournamentRoundLink.round_id == Round.id)
        .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
        .join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id)
        .join(Tee)
        .join(Track)
        .join(Course)
        .where(TournamentRoundLink.tournament_id == tournament_id)
    ).all()

    round_summaries = [
        RoundSummary(
            round_id=round.id,
            date_played=round.date_played,
            round_type=round.type,
            golfer_name=golfer.name,
            golfer_playing_handicap=round_golfer_link.playing_handicap,
            course_name=course.name,
            track_name=track.name,
            tee_name=tee.name,
            tee_gender=tee.gender,
            tee_par=tee.par,
            tee_rating=tee.rating,
            tee_slope=tee.slope,
            tee_color=tee.color if tee.color else "none",
        )
        for round, round_golfer_link, golfer, course, track, tee in round_query_data
    ]
    round_summaries.sort(key=lambda r: r.round_id)

    handicap_system = (
        APLLegacyHandicapSystem() if use_legacy_handicapping else APLHandicapSystem()
    )
    # TODO: Move get_hole_results to a database module
    hole_result_data = get_hole_results_for_rounds(
        session=session, round_ids=[r.round_id for r in round_summaries]
    )
    for r in round_summaries:
        round_holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in round_holes])
        r.gross_score = sum([h.gross_score for h in round_holes])
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in round_holes])
        r.net_score = sum([h.net_score for h in round_holes])
        r.score_differential = handicap_system.compute_score_differential(
            r.tee_rating, r.tee_slope, r.adjusted_gross_score
        )
    return round_summaries


def _compute_team_scores_best_ball(
    rounds: list[RoundResults], num_balls: int = 1
) -> tuple[float, float]:
    gross_score = 0
    net_score = 0
    for hole_num in np.unique([h.number for r in rounds for h in r.holes]):
        hole_gross_scores = [
            h.gross_score for r in rounds for h in r.holes if h.number == hole_num
        ]
        if len(hole_gross_scores) < num_balls:
            gross_score += sum(
                hole_gross_scores
            )  # TODO: handle "fewer golfers than n" case
        else:
            gross_score += sum(
                sorted(hole_gross_scores)[:num_balls]
            )  # take the "n" smallest scores

        hole_net_scores = [
            h.net_score for r in rounds for h in r.holes if h.number == hole_num
        ]
        if len(hole_net_scores) < num_balls:
            net_score += sum(
                hole_net_scores
            )  # TODO: handle "fewer golfers than n" case
        else:
            net_score += sum(sorted(hole_net_scores)[:num_balls])

    return gross_score, net_score


def _compute_team_scores_scramble(rounds: list[RoundResults]) -> tuple[float, float]:
    # NOTE: should only be one score per hole per team anyway
    return _compute_team_scores_best_ball(rounds=rounds, num_balls=1)


def _compute_individual_scores(rounds: list[RoundResults]) -> tuple[float, float]:
    gross_score = sum([r.gross_score for r in rounds])
    net_score = sum([r.net_score for r in rounds])
    return gross_score, net_score


def get_standings(session: Session, tournament_id: int) -> TournamentStandings:
    tournament_info = get_info(session=session, tournament_id=tournament_id)

    round_ids = session.exec(
        select(Round.id)
        .join(TournamentRoundLink, onclause=TournamentRoundLink.round_id == Round.id)
        .where(TournamentRoundLink.tournament_id == tournament_id)
    ).all()
    round_data = get_tournament_rounds(
        session=session, tournament_id=tournament_id, round_ids=round_ids
    )

    teams = get_teams(session=session, tournament_id=tournament_id)

    standings = TournamentStandings(tournament_id=tournament_id)

    for team in teams:
        team_rounds = [r for r in round_data if r.team_id == team.team_id]

        gross_score: int | None = None
        net_score: int | None = None
        if tournament_info.scramble:
            gross_score, net_score = _compute_team_scores_scramble(rounds=team_rounds)
        elif tournament_info.bestball > 0:
            gross_score, net_score = _compute_team_scores_best_ball(
                rounds=team_rounds, num_balls=tournament_info.bestball
            )

        if gross_score is not None and net_score is not None:
            standings.teams.append(
                TournamentStandingsTeam(
                    team_id=team.team_id,
                    team_name=team.name,
                    gross_score=gross_score,
                    net_score=net_score,
                )
            )

    # TODO: Sort team standings and determine positions

    if tournament_info.individual:
        for golfer_id in np.unique([r.golfer_id for r in round_data]):
            golfer_rounds = [r for r in round_data if r.golfer_id == golfer_id]

            indiv_gross, indiv_net = _compute_individual_scores(rounds=golfer_rounds)

            standings.golfers.append(
                TournamentStandingsGolfer(
                    golfer_id=golfer_rounds[0].golfer_id,
                    golfer_name=golfer_rounds[0].golfer_name,
                    golfer_playing_handicap=golfer_rounds[0].golfer_playing_handicap,
                    gross_score=indiv_gross,
                    net_score=indiv_net,
                )
            )

    # TODO: Sort individual standings and determine positions

    return standings


def get_statistics(session: Session, tournament_id: int) -> TournamentStatistics:
    match_summaries = get_round_summaries(session=session, tournament_id=tournament_id)
    match_data = session.exec(
        select(Match, Round, Golfer, TeamGolferLink)
        .join(MatchRoundLink, onclause=MatchRoundLink.match_id == Match.id)
        .join(Round, onclause=Round.id == MatchRoundLink.round_id)
        .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
        .join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id)
        .join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id)
        .where(Match.id.in_((match.match_id for match in match_summaries)))
        .where(TeamGolferLink.team_id.in_((Match.home_team_id, Match.away_team_id)))
    ).all()

    tournament_golfer_stats: dict[int, GolferStatistics] = {}
    for match, match_round, match_golfer, match_tgl in match_data:
        if match_golfer.id not in tournament_golfer_stats:
            tournament_golfer_stats[match_golfer.id] = GolferStatistics(
                golfer_id=match_golfer.id,
                golfer_name=match_golfer.name,
                golfer_team_id=match_tgl.team_id,
                golfer_team_role=match_tgl.role,
            )
        golfer_stats = tournament_golfer_stats[match_golfer.id]

        golfer_stats.num_matches += 1
        golfer_stats.num_rounds += 1  # TODO: track repeat rounds

        points_won = 0
        if golfer_stats.golfer_team_id == match.home_team_id:
            points_won = match.home_score
        elif golfer_stats.golfer_team_id == match.away_team_id:
            points_won = match.away_score
        golfer_stats.points_won += points_won
        golfer_stats.avg_points_won += (
            points_won - golfer_stats.avg_points_won
        ) / golfer_stats.num_matches

        par = 0
        gross_score = 0
        net_score = 0

        round_data = session.exec(
            select(HoleResult, Hole)
            .join(Hole, onclause=Hole.id == HoleResult.hole_id)
            .where(HoleResult.round_id == match_round.id)
        ).all()
        for hole_result, hole in round_data:
            golfer_stats.num_holes += 1

            par += hole.par

            # Gross scoring (hole)
            gross_score += hole_result.gross_score

            if hole_result.gross_score <= 1:
                golfer_stats.gross_scoring.num_aces += 1
            elif hole_result.gross_score == (hole.par - 3):
                golfer_stats.gross_scoring.num_albatrosses += 1
            elif hole_result.gross_score == (hole.par - 2):
                golfer_stats.gross_scoring.num_eagles += 1
            elif hole_result.gross_score == (hole.par - 1):
                golfer_stats.gross_scoring.num_birdies += 1
            elif hole_result.gross_score == hole.par:
                golfer_stats.gross_scoring.num_pars += 1
            elif hole_result.gross_score == (hole.par + 1):
                golfer_stats.gross_scoring.num_bogeys += 1
            elif hole_result.gross_score == (hole.par + 2):
                golfer_stats.gross_scoring.num_double_bogeys += 1
            elif hole_result.gross_score > (hole.par + 2):
                golfer_stats.gross_scoring.num_others += 1

            # Gross scoring (hole)
            net_score += hole_result.net_score

            if hole_result.net_score <= 1:
                golfer_stats.net_scoring.num_aces += 1
            elif hole_result.net_score == (hole.par - 3):
                golfer_stats.net_scoring.num_albatrosses += 1
            elif hole_result.net_score == (hole.par - 2):
                golfer_stats.net_scoring.num_eagles += 1
            elif hole_result.net_score == (hole.par - 1):
                golfer_stats.net_scoring.num_birdies += 1
            elif hole_result.net_score == hole.par:
                golfer_stats.net_scoring.num_pars += 1
            elif hole_result.net_score == (hole.par + 1):
                golfer_stats.net_scoring.num_bogeys += 1
            elif hole_result.net_score == (hole.par + 2):
                golfer_stats.net_scoring.num_double_bogeys += 1
            elif hole_result.net_score > (hole.par + 2):
                golfer_stats.net_scoring.num_others += 1

            # Scoring by hole type
            if hole.par == 3:
                golfer_stats.num_par_3_holes += 1
                golfer_stats.gross_scoring.avg_par_3_score += (
                    hole_result.gross_score - golfer_stats.gross_scoring.avg_par_3_score
                ) / golfer_stats.num_par_3_holes
                golfer_stats.net_scoring.avg_par_3_score += (
                    hole_result.net_score - golfer_stats.net_scoring.avg_par_3_score
                ) / golfer_stats.num_par_3_holes
            elif hole.par == 4:
                golfer_stats.num_par_4_holes += 1
                golfer_stats.gross_scoring.avg_par_4_score += (
                    hole_result.gross_score - golfer_stats.gross_scoring.avg_par_4_score
                ) / golfer_stats.num_par_4_holes
                golfer_stats.net_scoring.avg_par_4_score += (
                    hole_result.net_score - golfer_stats.net_scoring.avg_par_4_score
                ) / golfer_stats.num_par_4_holes
            elif hole.par == 5:
                golfer_stats.num_par_5_holes += 1
                golfer_stats.gross_scoring.avg_par_5_score += (
                    hole_result.gross_score - golfer_stats.gross_scoring.avg_par_5_score
                ) / golfer_stats.num_par_5_holes
                golfer_stats.net_scoring.avg_par_5_score += (
                    hole_result.net_score - golfer_stats.net_scoring.avg_par_5_score
                ) / golfer_stats.num_par_5_holes

        # Gross scoring (round)
        golfer_stats.gross_scoring.avg_score += (
            gross_score - golfer_stats.gross_scoring.avg_score
        ) / golfer_stats.num_rounds
        golfer_stats.gross_scoring.avg_score_to_par += (
            (gross_score - par) - golfer_stats.gross_scoring.avg_score_to_par
        ) / golfer_stats.num_rounds

        # Net scoring (round)
        golfer_stats.net_scoring.avg_score += (
            net_score - golfer_stats.net_scoring.avg_score
        ) / golfer_stats.num_rounds
        golfer_stats.net_scoring.avg_score_to_par += (
            (net_score - par) - golfer_stats.net_scoring.avg_score_to_par
        ) / golfer_stats.num_rounds

    tournament_stats = TournamentStatistics(
        tournament_id=tournament_id, golfers=list(tournament_golfer_stats.values())
    )
    tournament_stats.golfers.sort(key=lambda g: g.gross_scoring.avg_score)

    return tournament_stats
