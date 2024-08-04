from sqlmodel import Session, select

from app.models.handicap import HandicapIndex


def get_handicap_history_for_golfer(
    session: Session, golfer_id: int
) -> list[HandicapIndex]:
    """Get handicap index history for a specific golfer.

    Parameters
    ----------
    session (`Session`): Database session.

    """
    return list(
        session.exec(
            select(HandicapIndex)
            .where(HandicapIndex.golfer_id == golfer_id)
            .order_by(HandicapIndex.date_posted, HandicapIndex.round_number)
        )
    )
