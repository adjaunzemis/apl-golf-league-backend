import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import Session

from app.models.course import Course
from app.models.flight import Flight


@pytest.mark.parametrize(
    "name, year, course_id, divisions",
    [("Test Flight Name", 2021, 1, []), ("Test Flight Name", 2021, None, [])],
)
def test_create_flight(
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
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == name
    assert data["year"] == year
    assert data["course_id"] == course_id
    assert data["id"] is not None


@pytest.mark.parametrize(
    "name, year, course_id, divisions",
    [(None, 2021, 1, []), ("Test Flight Name", None, 1, [])],
)
def test_create_flight_incomplete(
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
        Flight(name="Test Flight 1", year=2021, course_id=1),
        Flight(name="Test Flight 2", year=2021, course_id=2),
    ]
    for flight in flights:
        session.add(flight)
    session.commit()

    response = client_unauthorized.get("/flights/")
    assert response.status_code == 200

    data = response.json()
    assert data["num_flights"] == len(flights)
    assert len(data["flights"]) == len(flights)
    print(data)
    for dIdx in range(len(data["flights"])):
        assert data["flights"][dIdx]["name"] == flights[dIdx].name
        assert data["flights"][dIdx]["year"] == flights[dIdx].year
        assert (
            data["flights"][dIdx]["course"]
            == [
                course.name
                for course in courses
                if course.id == flights[dIdx].course_id
            ][0]
        )
        assert data["flights"][dIdx]["id"] == flights[dIdx].id


def test_read_flight(session: Session, client_unauthorized: TestClient):
    course = Course(name="Test Course 1", year=2021, course_id=1)
    session.add(course)
    flight = Flight(name="Test Flight 1", year=2021, course_id=1)
    session.add(flight)
    session.commit()

    response = client_unauthorized.get(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == flight.name
    assert data["year"] == flight.year
    assert data["course_id"] == flight.course_id
    assert data["id"] == flight.id
    assert len(data["divisions"]) == 0
    assert len(data["teams"]) == 0


def test_delete_flight(session: Session, client_admin: TestClient):
    flight = Flight(name="Test Flight 1", year=2021, course_id=1)
    session.add(flight)
    session.commit()

    response = client_admin.delete(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_200_OK

    flight_db = session.get(Flight, flight.id)
    assert flight_db is None


def test_delete_flight_unauthorized(session: Session, client_unauthorized: TestClient):
    flight = Flight(name="Test Flight 1", year=2021, course_id=1)
    session.add(flight)
    session.commit()

    response = client_unauthorized.delete(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
