import pytest
from fastapi import status
from sqlmodel import Session

from app.models.seasons import Season


@pytest.fixture()
def session_with_seasons(session: Session):
    session.add(Season(year=2025, is_active=False))
    session.add(Season(year=2024, is_active=True))
    session.add(Season(year=2023, is_active=False))
    session.commit()
    yield session


def test_get_seasons(session_with_seasons, client_unauthorized):
    response = client_unauthorized.get("/seasons/")
    assert response.status_code == status.HTTP_200_OK
    seasons_api = [Season(**season_json) for season_json in response.json()]
    assert len(seasons_api) == 3


def test_get_season_by_year(session_with_seasons, client_unauthorized):
    response = client_unauthorized.get("/seasons/2024")
    assert response.status_code == status.HTTP_200_OK
    season_api = Season(**response.json())
    assert season_api.year == 2024
    assert season_api.is_active


def test_get_season_by_year_not_found(session_with_seasons, client_unauthorized):
    response = client_unauthorized.get("/seasons/1900")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_season_unauthorized(session_with_seasons, client_unauthorized):
    response = client_unauthorized.post("/seasons/", json={"year": 2026})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_season_non_admin(session_with_seasons, client_non_admin):
    response = client_non_admin.post("/seasons/", json={"year": 2026})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_season(session_with_seasons, client_admin):
    response = client_admin.post("/seasons/", json={"year": 2026})
    assert response.status_code == status.HTTP_200_OK
    season_api = Season(**response.json())
    assert season_api.year == 2026
    assert not season_api.is_active


def test_create_season_duplicate(session_with_seasons, client_admin):
    response = client_admin.post("/seasons/", json={"year": 2024})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_active_season(session_with_seasons, client_unauthorized):
    response = client_unauthorized.get("/seasons/active/")
    assert response.status_code == status.HTTP_200_OK
    active_season_api = Season(**response.json())
    assert active_season_api.is_active


def test_get_active_season_not_found(session, client_unauthorized):
    response = client_unauthorized.get("/seasons/active/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_set_active_season_unauthorized(session_with_seasons, client_unauthorized):
    response = client_unauthorized.patch("/seasons/active/2025")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_set_active_season_non_admin(session_with_seasons, client_non_admin):
    response = client_non_admin.patch("/seasons/active/2025")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_set_active_season(session_with_seasons, client_admin):
    response = client_admin.patch("/seasons/active/2025")
    assert response.status_code == status.HTTP_200_OK
    active_season_api = Season(**response.json())
    assert active_season_api.year == 2025
    assert active_season_api.is_active


def test_set_active_season_not_found(session_with_seasons, client_admin):
    response = client_admin.patch("/seasons/active/1900")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_season_unauthorized(session_with_seasons, client_unauthorized):
    response = client_unauthorized.delete("/seasons/2025")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_season_non_admin(session_with_seasons, client_non_admin):
    response = client_non_admin.delete("/seasons/2025")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_season(session_with_seasons, client_admin):
    response = client_admin.delete("/seasons/2025")
    assert response.status_code == status.HTTP_200_OK
    active_season_api = Season(**response.json())
    assert active_season_api.year == 2025
    assert not active_season_api.is_active


def test_delete_season_active(session_with_seasons, client_admin):
    response = client_admin.delete("/seasons/2024")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_season_not_found(session_with_seasons, client_admin):
    response = client_admin.delete("/seasons/1900")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
