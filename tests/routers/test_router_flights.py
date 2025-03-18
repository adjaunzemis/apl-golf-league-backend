from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.course import Course
from app.models.flight import Flight
from app.models.flight_team_link import FlightTeamLink
from app.models.team import Team


@pytest.mark.parametrize(
    "name, year, course_id, divisions, secretary, signup_start_date, signup_stop_date, start_date, weeks",
    [
        (
            "Test Flight Name",
            2021,
            1,
            [],
            "Test Secretary",
            datetime(2021, 3, 1),
            datetime(2021, 3, 15),
            datetime(2021, 4, 1),
            18,
        ),
        (
            "Test Flight Name",
            2021,
            None,
            [],
            "Test Secretary",
            datetime(2021, 3, 1),
            datetime(2021, 3, 15),
            datetime(2021, 4, 1),
            18,
        ),
    ],
)
def test_create_flight(
    client_admin: TestClient,
    name: str,
    year: int,
    course_id: int,
    divisions: list,
    secretary: str,
    signup_start_date: datetime,
    signup_stop_date: datetime,
    start_date: datetime,
    weeks: int,
):
    response = client_admin.post(
        "/flights/",
        json={
            "name": name,
            "year": year,
            "course_id": course_id,
            "divisions": divisions,
            "secretary": secretary,
            "signup_start_date": str(signup_start_date),
            "signup_stop_date": str(signup_stop_date),
            "start_date": str(start_date),
            "weeks": weeks,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == name
    assert data["year"] == year
    assert data["course_id"] == course_id
    assert data["id"] is not None


@pytest.mark.parametrize(
    "name, year, course_id, divisions, secretary, signup_start_date, signup_stop_date, start_date, weeks",
    [
        (
            None,
            2021,
            1,
            [],
            "Test Secretary",
            datetime(2021, 3, 1),
            datetime(2021, 3, 15),
            datetime(2021, 4, 1),
            18,
        ),
        (
            "Test Flight Name",
            None,
            1,
            [],
            "Test Secretary",
            datetime(2021, 3, 1),
            datetime(2021, 3, 15),
            datetime(2021, 4, 1),
            18,
        ),
        (
            "Test Flight Name",
            2021,
            1,
            [],
            None,
            datetime(2021, 3, 1),
            datetime(2021, 3, 15),
            datetime(2021, 4, 1),
            18,
        ),
        (
            "Test Flight Name",
            2021,
            1,
            [],
            "Test Secretary",
            None,
            datetime(2021, 3, 15),
            datetime(2021, 4, 1),
            18,
        ),
        (
            "Test Flight Name",
            2021,
            1,
            [],
            "Test Secretary",
            datetime(2021, 3, 1),
            None,
            datetime(2021, 4, 1),
            18,
        ),
        (
            "Test Flight Name",
            2021,
            1,
            [],
            "Test Secretary",
            datetime(2021, 3, 1),
            datetime(2021, 3, 15),
            None,
            18,
        ),
        (
            "Test Flight Name",
            2021,
            1,
            [],
            "Test Secretary",
            datetime(2021, 3, 1),
            datetime(2021, 3, 15),
            datetime(2021, 4, 1),
            None,
        ),
    ],
)
def test_create_flight_incomplete(
    client_admin: TestClient,
    name: str | None,
    year: int | None,
    course_id: int | None,
    divisions: list | None,
    secretary: str | None,
    signup_start_date: datetime | None,
    signup_stop_date: datetime | None,
    start_date: datetime | None,
    weeks: int | None,
):
    response = client_admin.post(
        "/flights/",
        json={
            "name": name,
            "year": year,
            "course_id": course_id,
            "divisions": divisions,
            "secretary": secretary,
            "signup_start_date": str(signup_start_date),
            "signup_stop_date": str(signup_stop_date),
            "start_date": str(start_date),
            "weeks": weeks,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "name, year, course_id, divisions",
    [
        ({"key": "value"}, 2021, 1, []),
        ("Test Flight Name", {"key": "value"}, 1, []),
        ("Test Flight Name", 2021, {"key": "value"}, []),
        ("Test Flight Name", 2021, 1, {"key": "value"}),
    ],
)
def test_create_flight_invalid(
    client_admin: TestClient, name: str, year: int, course_id: int, divisions: list
):
    response = client_admin.post(
        "/flights/",
        json={
            "name": name,
            "year": year,
            "course_id": course_id,
            "divisions": divisions,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "name, year, course_id, divisions",
    [("Test Flight Name", 2021, 1, []), ("Test Flight Name", 2021, None, [])],
)
def test_create_flight_unauthorized(
    client_unauthorized: TestClient,
    name: str,
    year: int,
    course_id: int,
    divisions: list,
):
    response = client_unauthorized.post(
        "/flights/",
        json={
            "name": name,
            "year": year,
            "course_id": course_id,
            "divisions": divisions,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_flights(session: Session, client_unauthorized: TestClient):
    courses = [
        Course(name="Test Course 1", year=2021, course_id=1),
        Course(name="Test Course 2", year=2021, course_id=2),
    ]
    for course in courses:
        session.add(course)

    flights = [
        Flight(
            name="Test Flight 1",
            year=2021,
            course_id=1,
            secretary="Test Secretary",
            signup_start_date=datetime(2021, 3, 1),
            signup_stop_date=datetime(2021, 3, 15),
            start_date=datetime(2021, 4, 1),
            weeks=18,
        ),
        Flight(
            name="Test Flight 2",
            year=2021,
            course_id=2,
            secretary="Test Secretary",
            signup_start_date=datetime(2021, 3, 1),
            signup_stop_date=datetime(2021, 3, 15),
            start_date=datetime(2021, 4, 1),
            weeks=18,
        ),
    ]
    for flight in flights:
        session.add(flight)
    session.commit()

    response = client_unauthorized.get("/flights/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == len(flights)

    for idx, flight_json in enumerate(data):
        assert flight_json["name"] == flights[idx].name
        assert flight_json["year"] == flights[idx].year
        assert (
            flight_json["course"]
            == [
                course.name for course in courses if course.id == flights[idx].course_id
            ][0]
        )
        assert flight_json["id"] == flights[idx].id


def test_read_flight(session: Session, client_unauthorized: TestClient):
    course = Course(name="Test Course 1", year=2021)
    session.add(course)
    session.commit()
    session.refresh(course)
    flight = Flight(
        name="Test Flight 1",
        year=2021,
        course_id=course.id,
        secretary="Test Secretary",
        signup_start_date=datetime(2021, 3, 1),
        signup_stop_date=datetime(2021, 3, 15),
        start_date=datetime(2021, 4, 1),
        weeks=18,
    )
    session.add(flight)
    team = Team(name="Test Team 1")
    session.add(team)
    session.commit()
    session.refresh(team)
    session.refresh(flight)
    flightteamlink = FlightTeamLink(flight_id=flight.id, team_id=team.id)
    session.add(flightteamlink)
    session.commit()

    response = client_unauthorized.get(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == flight.name
    assert data["year"] == flight.year
    assert data["course_id"] == flight.course_id
    assert data["id"] == flight.id
    assert len(data["divisions"]) == 0
    assert len(data["teams"]) == 1


def test_delete_flight(session: Session, client_admin: TestClient):
    flight = Flight(
        name="Test Flight 1",
        year=2021,
        course_id=1,
        secretary="Test Secretary",
        signup_start_date=datetime(2021, 3, 1),
        signup_stop_date=datetime(2021, 3, 15),
        start_date=datetime(2021, 4, 1),
        weeks=18,
    )
    session.add(flight)
    session.commit()

    response = client_admin.delete(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_200_OK

    flight_db = session.get(Flight, flight.id)
    assert flight_db is None


def test_delete_flight_unauthorized(session: Session, client_unauthorized: TestClient):
    flight = Flight(
        name="Test Flight 1",
        year=2021,
        course_id=1,
        secretary="Test Secretary",
        signup_start_date=datetime(2021, 3, 1),
        signup_stop_date=datetime(2021, 3, 15),
        start_date=datetime(2021, 4, 1),
        weeks=18,
    )
    session.add(flight)
    session.commit()

    response = client_unauthorized.delete(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
