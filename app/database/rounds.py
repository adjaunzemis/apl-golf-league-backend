from sqlmodel import Session, or_, select

from app.models.course import Course
from app.models.golfer import Golfer
from app.models.hole import Hole
from app.models.hole_result import HoleResult, HoleResultData
from app.models.match import Match
from app.models.match_round_link import MatchRoundLink
from app.models.round import Round, RoundData
from app.models.round_golfer_link import RoundGolferLink
from app.models.team import Team
from app.models.tee import Tee
from app.models.track import Track
from app.utilities.apl_handicap_system import APLHandicapSystem
from app.utilities.handicap_system import HandicapSystem


def get_hole_results_for_rounds(
    session: Session, round_ids: list[int]
) -> list[HoleResultData]:
    # TODO: Simplify using HoleResultRead* classes?
    hole_query_data = session.exec(
        select(HoleResult, Hole).join(Hole).where(HoleResult.round_id.in_(round_ids))
    )
    hole_result_data = [
        HoleResultData(
            hole_result_id=hole_result.id,
            round_id=hole_result.round_id,
            hole_id=hole_result.hole_id,
            number=hole.number,
            par=hole.par,
            yardage=hole.yardage,
            stroke_index=hole.stroke_index,
            handicap_strokes=hole_result.handicap_strokes,
            gross_score=hole_result.gross_score,
            adjusted_gross_score=hole_result.adjusted_gross_score,
            net_score=hole_result.net_score,
        )
        for hole_result, hole in hole_query_data
    ]
    return sorted(hole_result_data, key=lambda h: h.number)


def get_flight_round_data(
    session: Session,
    round_ids: list[int],
    handicap_system: HandicapSystem = APLHandicapSystem(),
) -> list[RoundData]:
    round_query_data = session.exec(
        select(Round, RoundGolferLink, Golfer, Tee, Track, Course, MatchRoundLink, Team)
        .join(RoundGolferLink, onclause=(RoundGolferLink.round_id == Round.id))
        .join(Golfer, onclause=(Golfer.id == RoundGolferLink.golfer_id))
        .join(Tee)
        .join(Track)
        .join(Course)
        .join(MatchRoundLink, onclause=MatchRoundLink.round_id == Round.id)
        .join(Match, onclause=(Match.id == MatchRoundLink.match_id))
        .join(
            Team,
            onclause=or_(Team.id == Match.home_team_id, Team.id == Match.away_team_id),
        )
        .where(Round.id.in_(round_ids))
    )

    round_data = [
        RoundData(
            round_id=round.id,
            match_id=match_round_link.match_id,
            team_id=team.id,
            round_type=round.type,
            date_played=round.date_played,
            date_updated=round.date_updated,
            golfer_id=round_golfer_link.golfer_id,
            golfer_name=golfer.name,
            golfer_playing_handicap=round_golfer_link.playing_handicap,
            team_name=team.name,
            course_id=course.id,
            course_name=course.name,
            track_id=track.id,
            track_name=track.name,
            tee_id=tee.id,
            tee_name=tee.name,
            tee_gender=tee.gender,
            tee_par=tee.par,
            tee_rating=tee.rating,
            tee_slope=tee.slope,
            tee_color=tee.color if tee.color else "none",
        )
        for round, round_golfer_link, golfer, tee, track, course, match_round_link, team in round_query_data
    ]

    hole_result_data = get_hole_results_for_rounds(
        session=session, round_ids=[r.round_id for r in round_data]
    )

    # Add hole data to round data and return
    for r in round_data:
        r.holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in r.holes])
        r.gross_score = sum([h.gross_score for h in r.holes])
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in r.holes])
        r.net_score = sum([h.net_score for h in r.holes])
        r.score_differential = handicap_system.compute_score_differential(
            r.tee_rating, r.tee_slope, r.adjusted_gross_score
        )
    return round_data
