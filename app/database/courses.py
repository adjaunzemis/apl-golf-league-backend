from sqlmodel import Session, select

from app.models.course import Course
from app.models.hole import Hole
from app.models.tee import Tee
from app.models.track import Track


def get_courses_by_id(session: Session, ids: list[int]) -> list[Course]:
    """Get courses from database with given identifiers.

    Parameters
    ----------
    session (`Session`): Database session.
    ids (list[int]): Course identifiers to query.

    Returns
    -------
    list[`Course`]: Courses from database.
    """
    return list(session.exec(select(Course).where(Course.id.in_(ids))).all())


def get_tracks_by_id(session: Session, ids: list[int]) -> list[Track]:
    """Get tracks from database with given identifiers.

    Parameters
    ----------
    session (`Session`): Database session.
    ids (list[int]): Track identifiers to query.

    Returns
    -------
    list[`Track`]: Tracks from database.
    """
    return list(session.exec(select(Track).where(Track.id.in_(ids))).all())


def get_tees_by_id(session: Session, ids: list[int]) -> list[Tee]:
    """Get tees from database with given identifiers.

    Parameters
    ----------
    session (`Session`): Database session.
    ids (list[int]): Tee identifiers to query.

    Returns
    -------
    list[`Tee`]: Tees from database.
    """
    return list(session.exec(select(Tee).where(Tee.id.in_(ids))).all())


def get_holes_by_id(session: Session, ids: list[int]) -> list[Hole]:
    """Get holes from database with given identifiers.

    Parameters
    ----------
    session (`Session`): Database session.
    ids (list[int]): Hole identifiers to query.

    Returns
    -------
    list[`Hole`]: Holes from database.
    """
    return list(session.exec(select(Hole).where(Hole.id.in_(ids))).all())


def get_holes_by_tee_id(session: Session, tee_id: int) -> list[Hole]:
    """Get holes from database for the given tee set.

    Parameters
    ----------
    tee_id (int): Tee identifier.

    Returns
    -------
    list['Hole']: Holes for this tee set from database.
    """
    return list(session.exec(select(Hole).where(Hole.tee_id == tee_id)).all())


def get_course_data_by_tee_id(
    session: Session, tee_id: int
) -> tuple[Course, Track, Tee, list[Hole]]:
    """Get course, track, tee, and hole data for the given tee set.

    Parameters
    ----------
    session (`Session`): Database session.
    tee_id (int): Tee identifier.

    Returns
    -------
    tuple[Course, Track, Tee, list[Hole]] | None: Course, track, tee, and hole data from database.
    """
    tee_db = next(iter(get_tees_by_id(session=session, ids=[tee_id])), None)
    if tee_db is None:
        raise ValueError(f"Unable to find tee with id={tee_id}")

    track_db = next(
        iter(get_tracks_by_id(session=session, ids=[tee_db.track_id])), None
    )
    if track_db is None:
        raise ValueError(f"Unable to find track with id={tee_db.track_id}")

    course_db = next(
        iter(get_courses_by_id(session=session, ids=[track_db.course_id])), None
    )
    if course_db is None:
        raise ValueError(f"Unable to find course with id={track_db.course_id}")

    holes_db = get_holes_by_tee_id(session=session, tee_id=tee_id)

    return (course_db, track_db, tee_db, holes_db)
