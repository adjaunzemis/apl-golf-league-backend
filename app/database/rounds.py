from sqlmodel import Session, select

from app.models.course import Course
from app.models.golfer import Golfer
from app.models.round import Round, RoundResults
from app.models.round_golfer_link import RoundGolferLink
from app.models.tee import Tee
from app.models.track import Track


def get_rounds_by_id(session: Session, ids: list[int]) -> list[Round]:
    """Get rounds from database with given identifiers.

    Round is just metadata about the round (e.g. where/when it was played), not scoring.

    Parameters
    ----------
    session (`Session`): Database session.
    ids (list[int]): Round identifiers to query.

    Returns
    -------
    list[`Round`]: Rounds from database.
    """
    return list(session.exec(select(Round).where(Round.id.in_(ids))).all())


def get_round_results_by_id(session: Session, ids: list[int]) -> list[RoundResults]:
    """Get round results from database by given identifiers.

    Round results includes metadata about round as well as scoring and golfer information.

    Parameters
    ----------
    session (`Session`): Database session.
    ids (list[int]): Round identifiers.

    Returns
    -------
    list[`RoundResults`]: Round results from database.
    """
    rounds_db = get_rounds_by_id(session=session, ids=ids)

    course_data_db = session.exec(
        select(Course, Track, Tee)
        .join(Tee)
        .join(Track)
        .join(Course)
        .where(Round.id == id)
    ).one_or_none()

    if round_data_db is None:
        return None

    round_db, course_db, track_db, tee_db = round_data_db

    golfer_data_db = session.exec(
        select(RoundGolferLink, Golfer)
        .join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id)
        .where(RoundGolferLink.round_id == round_db.id)
    ).one_or_none()

    if round_golfer_data_db is None:
        return None

    round_golfer_link_db, golfer_db = round_golfer_data_db

    round_data = RoundResults(
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
    )
