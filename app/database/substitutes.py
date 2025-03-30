from sqlmodel import Session, select

from app.models.substitutes import Substitute, SubstituteCreate


def get_substitute(
    session: Session, flight_id: int, golfer_id: int
) -> Substitute | None:
    return session.exec(
        select(Substitute)
        .where(Substitute.flight_id == flight_id)
        .where(Substitute.golfer_id == golfer_id)
    ).one_or_none()


def get_substitutes(session: Session, flight_id: int | None = None) -> list[Substitute]:
    query = select(Substitute).order_by(Substitute.flight_id)
    if flight_id is not None:
        query = query.where(Substitute.flight_id == flight_id)
    return list(session.exec(query).all())


def create_substitute(
    session: Session, new_substitute: SubstituteCreate
) -> Substitute | None:
    substitute_db = get_substitute(
        session=session,
        flight_id=new_substitute.flight_id,
        golfer_id=new_substitute.golfer_id,
    )
    if substitute_db is not None:
        return None
    substitute_db = Substitute.model_validate(new_substitute)
    session.add(substitute_db)
    session.commit()
    session.refresh(substitute_db)
    return substitute_db


def delete_substitute(
    session: Session, flight_id: int, golfer_id: int
) -> Substitute | None:
    substitute_db = get_substitute(
        session=session, flight_id=flight_id, golfer_id=golfer_id
    )
    if substitute_db is None:
        return None
    session.delete(substitute_db)
    session.commit()
    return substitute_db
