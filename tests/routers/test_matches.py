import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.match import Match


@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score",
    [
        (1, 1, 1, 2, 7.5, 3.5),
        (1, 1, 1, 2, 7.5, None),
        (1, 1, 1, 2, None, 3.5),
        (1, 1, 1, 2, None, None),
    ],
)
def test_create_match(
    client_admin: TestClient,
    flight_id: int,
    week: int,
    home_team_id: int,
    away_team_id: int,
    home_score: float,
    away_score: float,
):
    response = client_admin.post(
        "/matches/",
        json={
            "flight_id": flight_id,
            "week": week,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_score": home_score,
            "away_score": away_score,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["flight_id"] == flight_id
    assert data["week"] == week
    assert data["home_team_id"] == home_team_id
    assert data["away_team_id"] == away_team_id
    assert data["home_score"] == home_score
    assert data["away_score"] == away_score
    assert data["id"] is not None


@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score",
    [(1, None, 1, 2, 7.5, 3.5)],
)
def test_create_match_unauthorized(
    client_unauthorized: TestClient,
    flight_id: int,
    week: int,
    home_team_id: int,
    away_team_id: int,
    home_score: float,
    away_score: float,
):
    response = client_unauthorized.post(
        "/matches/",
        json={
            "flight_id": flight_id,
            "week": week,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_score": home_score,
            "away_score": away_score,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score",
    [(1, None, 1, 2, 7.5, 3.5)],
)
def test_create_match_incomplete(
    client_admin: TestClient,
    flight_id: int,
    week: int,
    home_team_id: int,
    away_team_id: int,
    home_score: float,
    away_score: float,
):
    response = client_admin.post(
        "/matches/",
        json={
            "flight_id": flight_id,
            "week": week,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_score": home_score,
            "away_score": away_score,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score",
    [
        ({"key": "value"}, 1, 1, 2, 7.5, 3.5),
        (1, {"key": "value"}, 1, 2, 7.5, 3.5),
        (1, 1, {"key": "value"}, 2, 7.5, 3.5),
        (1, 1, 1, {"key": "value"}, 7.5, 3.5),
        (1, 1, 1, 2, {"key": "value"}, 3.5),
        (1, 1, 1, 2, 7.5, {"key": "value"}),
    ],
)
def test_create_match_invalid(
    client_admin: TestClient,
    flight_id: int,
    week: int,
    home_team_id: int,
    away_team_id: int,
    home_score: float,
    away_score: float,
):
    # Invalid input data types
    response = client_admin.post(
        "/matches/",
        json={
            "flight_id": flight_id,
            "week": week,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_score": home_score,
            "away_score": away_score,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_match(session: Session, client_admin: TestClient):
    match = Match(flight_id=1, week=1, home_team_id=1, away_team_id=2)
    session.add(match)
    session.commit()

    response = client_admin.patch(
        f"/matches/{match.id}", json={"home_score": 7.5, "away_score": 3.5}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["flight_id"] == match.flight_id
    assert data["week"] == match.week
    assert data["home_team_id"] == match.home_team_id
    assert data["away_team_id"] == match.away_team_id
    assert data["home_score"] == 7.5
    assert data["away_score"] == 3.5
    assert data["id"] == match.id


def test_delete_match(session: Session, client_admin: TestClient):
    match = Match(flight_id=1, week=1, home_team_id=1, away_team_id=2)
    session.add(match)
    session.commit()

    response = client_admin.delete(f"/matches/{match.id}")
    assert response.status_code == status.HTTP_200_OK

    match_db = session.get(Match, match.id)
    assert match_db is None


def test_delete_match_unauthorized(session: Session, client_unauthorized: TestClient):
    match = Match(flight_id=1, week=1, home_team_id=1, away_team_id=2)
    session.add(match)
    session.commit()

    response = client_unauthorized.delete(f"/matches/{match.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
