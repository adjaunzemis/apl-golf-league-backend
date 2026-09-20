from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.flight import Flight
from app.models.flight_team_link import FlightTeamLink
from app.models.match import Match
from app.models.team import Team


@pytest.fixture()
def session_with_flight_and_teams(session: Session):
    flight = Flight(
        name="Test Flight",
        year=2026,
        secretary="Test Secretary",
        signup_start_date=datetime(2026, 1, 1),
        signup_stop_date=datetime(2026, 1, 14),
        start_date=datetime(2026, 1, 21),
        weeks=10,
    )
    session.add(flight)
    session.commit()
    session.refresh(flight)

    team_1 = Team(name="Test Team 1")
    session.add(team_1)
    team_2 = Team(name="Test Team 2")
    session.add(team_2)
    session.commit()
    session.refresh(team_1)
    session.refresh(team_2)

    session.add(FlightTeamLink(flight_id=flight.id, team_id=team_1.id))
    session.add(FlightTeamLink(flight_id=flight.id, team_id=team_2.id))
    session.commit()

    yield session


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
    session_with_flight_and_teams: Session,
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
    [(1, 1, 1, 2, 7.5, 3.5)],
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
    [(1, 1, 1, 2, 7.5, 3.5)],
)
def test_create_match_non_admin(
    client_non_admin: TestClient,
    flight_id: int,
    week: int,
    home_team_id: int,
    away_team_id: int,
    home_score: float,
    away_score: float,
):
    response = client_non_admin.post(
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
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


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
def test_create_match_unprocessable(
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
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score, expected_status, expected_detail",
    [
        (2, 1, 1, 2, 7.5, 3.5, status.HTTP_404_NOT_FOUND, "Unable to find flight"),
        (
            1,
            11,
            1,
            2,
            7.5,
            3.5,
            status.HTTP_400_BAD_REQUEST,
            "Unable to create match on week",
        ),
        (1, 1, 3, 2, 7.5, 3.5, status.HTTP_404_NOT_FOUND, "Unable to find home team"),
        (1, 1, 1, 3, 7.5, 3.5, status.HTTP_404_NOT_FOUND, "Unable to find away team"),
    ],
)
def test_create_match_invalid(
    session_with_flight_and_teams: Session,
    client_admin: TestClient,
    flight_id: int,
    week: int,
    home_team_id: int,
    away_team_id: int,
    home_score: float,
    away_score: float,
    expected_status: int,
    expected_detail: str,
):
    # Invalid match data
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
    assert response.status_code == expected_status
    assert expected_detail in response.json()["detail"]


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
