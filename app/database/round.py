from sqlmodel import Session, select

from app.models.round import Round


def get_rounds_by_id(session: Session, ids: list[int]) -> list[Round]:
    """Get rounds from database with given identifiers.

    Parameters
    ----------
    session (`Session`): Database session.
    ids (list[int]): Round identifiers to query.

    Returns
    -------
    list[`Round`]: Rounds from database.
    """
    return list(session.exec(select(Round).where(Round.id.in_(ids))).all())
