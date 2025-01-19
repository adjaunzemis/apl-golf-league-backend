import pytest
from sqlmodel import Session, select

from app.database import seasons as db_seasons
from app.models.seasons import Season, SeasonCreate


@pytest.fixture()
def session_with_seasons(session: Session):
    session.add(Season(year=2025, is_active=False))
    session.add(Season(year=2024, is_active=True))
    session.add(Season(year=2023, is_active=False))
    session.commit()
    yield session


def test_get_seasons(session_with_seasons):
    result = db_seasons.get_seasons(session_with_seasons)
    assert len(result) == 3


def test_get_season_by_year(session_with_seasons):
    result = db_seasons.get_season_by_year(session_with_seasons, 2024)
    assert result.year == 2024
    assert result.is_active


def test_get_season_by_year_not_found(session_with_seasons):
    result = db_seasons.get_season_by_year(session_with_seasons, 1900)
    assert result is None


def test_create_season(session_with_seasons):
    new_season = SeasonCreate(year=2026)
    season_db = db_seasons.create_season(session_with_seasons, new_season)
    assert season_db.year == new_season.year
    assert not season_db.is_active


def test_create_season_duplicate(session_with_seasons):
    new_season = SeasonCreate(year=2024)
    season_db = db_seasons.create_season(session_with_seasons, new_season)
    assert season_db is None


def test_get_active_season(session_with_seasons):
    active_season = db_seasons.get_active_season(session_with_seasons)
    assert active_season.is_active


def test_get_active_season_not_found(session):
    active_season = db_seasons.get_active_season(session)
    assert active_season is None


def test_set_active_season(session_with_seasons):
    active_season = db_seasons.set_active_season(session_with_seasons, 2025)
    assert active_season.year == 2025
    assert active_season.is_active
    active_seasons_db = list(
        session_with_seasons.exec(select(Season).where(Season.is_active == True)).all()
    )
    assert len(active_seasons_db) == 1
    assert active_seasons_db[0].year == 2025


def test_set_active_season_not_found(session_with_seasons):
    active_season = db_seasons.set_active_season(session_with_seasons, 1900)
    assert active_season is None


def test_delete_season_active(session_with_seasons):
    season = db_seasons.delete_season(session_with_seasons, 2025)
    assert season.year == 2025
    assert not season.is_active
    season_db = session_with_seasons.exec(
        select(Season).where(Season.year == 2025)
    ).one_or_none()
    assert season_db is None


def test_delete_season_active(session_with_seasons):
    season = db_seasons.delete_season(session_with_seasons, 2024)
    assert season is None


def test_delete_season_not_found(session_with_seasons):
    season = db_seasons.delete_season(session_with_seasons, 1900)
    assert season is None
