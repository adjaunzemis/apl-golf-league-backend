from sqlmodel import Session, asc, select

from app.database import courses as db_courses
from app.models.golfer import Golfer
from app.models.hole import Hole
from app.models.hole_result import HoleResult, HoleResultData
from app.models.round import Round, RoundResults
from app.models.round_golfer_link import RoundGolferLink
from app.utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem
from app.utilities.handicap_system import HandicapSystem


def get_rounds_by_id(session: Session, round_ids: list[int]) -> list[Round]:
    """Get rounds from database with given identifiers.

    Round is just metadata about the round (e.g. where/when it was played), not scoring.

    Parameters
    ----------
    session (`Session`): Database session.
    round_ids (list[int]): Round identifiers to query.

    Returns
    -------
    list[`Round`]: Rounds from database.
    """
    return list(session.exec(select(Round).where(Round.id.in_(round_ids))).all())


def get_golfer_data_for_round(
    session: Session, round_id: int
) -> list[tuple[RoundGolferLink, Golfer]]:
    """Gets golfer data for a given round.

    Golfer data includes metadata aboue that golfer as well as specific data for that round, e.g. playing handicap.

    Parameters
    ----------
    session (`Session`): Database session.
    round_id (int): Round identifier to query.

    Returns
    -------
    list[tuple[Golfer, RoundGolferLink]]: Golfer data for this round.
    """
    return list(
        session.exec(
            select(RoundGolferLink, Golfer)
            .join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id)
            .where(RoundGolferLink.round_id == round_id)
        ).all()
    )


def get_hole_results_for_rounds(
    session: Session, round_ids: list[int]
) -> list[HoleResultData]:
    """Gets hole result data for the given rounds.

    Parameters
    ----------
    session (`Session`): Database session.
    round_id (list[int]): Round identifiers to query.

    Returns
    -------
    list[HoleResultData]: Hole results for the given rounds.
    """
    # TODO: Simplify using HoleResultRead* classes
    hole_query_data = session.exec(
        select(HoleResult, Hole)
        .join(Hole)
        .where(HoleResult.round_id.in_(round_ids))
        .order_by(asc(HoleResult.round_id), asc(Hole.number))
    )
    return [
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


def get_round_results_by_id(
    session: Session,
    round_ids: list[int],
    handicap_system: HandicapSystem = APLLegacyHandicapSystem(),
) -> list[RoundResults]:
    """Get round results from database by given identifiers.

    Round results includes metadata about round as well as scoring and golfer information.

    Parameters
    ----------
    session (`Session`): Database session.
    round_ids (list[int]): Round identifiers.
    handicap_system (`HandicapSystem`): Handicap system to use for computing hole results.

    Returns
    -------
    list[`RoundResults`]: Round results from database.
    """
    rounds_db = get_rounds_by_id(session=session, round_ids=round_ids)

    course_data_db = {
        round_db.id: db_courses.get_course_data_by_tee_id(
            session=session, tee_id=round_db.tee_id
        )
        for round_db in rounds_db
    }

    golfer_data_db = {
        round_db.id: get_golfer_data_for_round(session=session, round_id=round_db.id)
        for round_db in rounds_db
    }

    hole_results_db = get_hole_results_for_rounds(session=session, round_ids=round_ids)

    round_results: list[RoundResults] = []
    for round_db in rounds_db:
        if round_db.id not in course_data_db or round_db.id not in golfer_data_db:
            continue

        course_db, track_db, tee_db, _ = course_data_db[round_db.id]

        round_hole_results_db = [
            h for h in hole_results_db if h.round_id == round_db.id
        ]
        gross_score = sum([h.gross_score for h in round_hole_results_db])
        adjusted_gross_score = sum(
            [h.adjusted_gross_score for h in round_hole_results_db]
        )
        net_score = sum([h.net_score for h in round_hole_results_db])
        score_differential = handicap_system.compute_score_differential(
            tee_db.rating, tee_db.slope, adjusted_gross_score
        )

        for round_golfer_link_db, golfer_db in golfer_data_db[round_db.id]:
            round_results.append(
                RoundResults(
                    round_id=round_db.id,
                    round_type=round_db.type,
                    date_played=round_db.date_played,
                    date_updated=round_db.date_updated,
                    golfer_id=round_golfer_link_db.golfer_id,
                    golfer_name=golfer_db.name,
                    golfer_playing_handicap=round_golfer_link_db.playing_handicap,
                    course_id=course_db.id,
                    course_name=course_db.name,
                    track_id=track_db.id,
                    track_name=track_db.name,
                    tee_id=tee_db.id,
                    tee_name=tee_db.name,
                    tee_gender=tee_db.gender,
                    tee_par=tee_db.par,
                    tee_rating=tee_db.rating,
                    tee_slope=tee_db.slope,
                    tee_color=tee_db.color if tee_db.color else "none",
                    holes=round_hole_results_db,
                    gross_score=gross_score,
                    adjusted_gross_score=adjusted_gross_score,
                    net_score=net_score,
                    score_differential=score_differential,
                )
            )

    return round_results
