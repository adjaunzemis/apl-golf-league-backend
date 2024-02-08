import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api import app
from app.dependencies import get_current_user, get_sql_db_session
from app.models.course import Course
from app.models.flight import Flight
from app.models.user import User


async def override_get_current_user_admin():
    return User(username="test_user", is_admin=True, disabled=False)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_sql_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "name, year, course_id, divisions",
    [("Test Flight Name", 2021, 1, []), ("Test Flight Name", 2021, None, [])],
)
def test_create_flight(
    client: TestClient, name: str, year: int, course_id: int, divisions: list
):
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    response = client.post(
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

    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "name, year, course_id, divisions",
    [(None, 2021, 1, []), ("Test Flight Name", None, 1, [])],
)
def test_create_flight_incomplete(
    client: TestClient, name: str, year: int, course_id: int, divisions: list
):
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    response = client.post(
        "/flights/",
        json={
            "name": name,
            "year": year,
            "course_id": course_id,
            "divisions": divisions,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    app.dependency_overrides.clear()


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
    client: TestClient, name: str, year: int, course_id: int, divisions: list
):
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    response = client.post(
        "/flights/",
        json={
            "name": name,
            "year": year,
            "course_id": course_id,
            "divisions": divisions,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "name, year, course_id, divisions",
    [("Test Flight Name", 2021, 1, []), ("Test Flight Name", 2021, None, [])],
)
def test_create_flight_unauthorized(
    client: TestClient, name: str, year: int, course_id: int, divisions: list
):
    response = client.post(
        "/flights/",
        json={
            "name": name,
            "year": year,
            "course_id": course_id,
            "divisions": divisions,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_read_flights(session: Session, client: TestClient):
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

    response = client.get("/flights/")
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


def test_read_flight(session: Session, client: TestClient):
    course = Course(name="Test Course 1", year=2021, course_id=1)
    session.add(course)
    flight = Flight(name="Test Flight 1", year=2021, course_id=1)
    session.add(flight)
    session.commit()

    response = client.get(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == flight.name
    assert data["year"] == flight.year
    assert data["course_id"] == flight.course_id
    assert data["id"] == flight.id
    assert len(data["divisions"]) == 0
    assert len(data["teams"]) == 0


def test_delete_flight(session: Session, client: TestClient):
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    flight = Flight(name="Test Flight 1", year=2021, course_id=1)
    session.add(flight)
    session.commit()

    response = client.delete(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_200_OK

    flight_db = session.get(Flight, flight.id)
    assert flight_db is None

    app.dependency_overrides.clear()


def test_delete_flight_unauthorized(session: Session, client: TestClient):
    flight = Flight(name="Test Flight 1", year=2021, course_id=1)
    session.add(flight)
    session.commit()

    response = client.delete(f"/flights/{flight.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
