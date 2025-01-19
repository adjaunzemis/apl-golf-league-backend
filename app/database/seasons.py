from sqlmodel import Session, desc, select

from app.models.seasons import Season, SeasonCreate


def get_seasons(session: Session) -> list[Season]:
    return list(session.exec(select(Season).order_by(desc(Season.year))).all())


def get_season_by_year(session: Session, year: int) -> Season | None:
    return session.exec(select(Season).where(Season.year == year)).one_or_none()


def create_season(session: Session, new_season: SeasonCreate) -> Season | None:
    if get_season_by_year(session, new_season.year) is not None:
        return None
    season_db = Season.model_validate(new_season)
    session.add(season_db)
    session.commit()
    session.refresh(season_db)
    return season_db


def get_active_season(session: Session) -> Season | None:
    return session.exec(
        select(Season)
        .where(Season.is_active == True)
        .order_by(desc(Season.year))
        .limit(1)
    ).one_or_none()


def set_active_season(session: Session, year: int) -> Season | None:
    season_db = session.exec(select(Season).where(Season.year == year)).one_or_none()
    if season_db is None:
        return None

    # Set current active season to inactive
    active_season_db = get_active_season(session)
    active_season_db.is_active = False
    session.add(active_season_db)

    # Set given season to active
    season_db.is_active = True
    session.add(season_db)
    session.commit()
    session.refresh(season_db)
    return season_db


def delete_season(session: Session, year: int) -> Season | None:
    season_db = session.exec(select(Season).where(Season.year == year)).one_or_none()
    if season_db is None or season_db.is_active:
        return None
    session.delete(season_db)
    session.commit()
    return season_db
