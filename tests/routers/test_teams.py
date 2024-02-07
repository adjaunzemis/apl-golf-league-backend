import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api import app
from app.dependencies import get_current_user, get_sql_db_session
from app.models.division import Division
from app.models.flight import Flight
from app.models.flight_division_link import FlightDivisionLink
from app.models.golfer import Golfer
from app.models.payment import LeagueDues, LeagueDuesType
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink, TeamRole
from app.models.tee import TeeGender
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


def test_create_team_without_flight_or_tournament(client: TestClient):
    response = client.post(
        "/teams/", json={"name": "Test Team Name", "golfer_data": []}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "name, flight_id, golfer_data",
    [
        (
            "Test Team Name",
            1,
            [
                {
                    "golfer_id": 1,
                    "golfer_name": "Test Golfer",
                    "division_id": 1,
                    "role": TeamRole.CAPTAIN,
                }
            ],
        )
    ],
)
def test_create_team_flight(
    session: Session, client: TestClient, name: str, flight_id: int, golfer_data: list
):
    for g in golfer_data:
        session.add(Golfer(name=g["golfer_name"]))

    session.add(Flight(name="Test Flight", year=2021, id=flight_id))
    session.add(LeagueDues(year=2021, type=LeagueDuesType.FLIGHT_DUES, amount=50))

    session.commit()

    response = client.post(
        "/teams/",
        json={"name": name, "flight_id": flight_id, "golfer_data": golfer_data},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == name
    assert data["id"] is not None


@pytest.mark.parametrize(
    "name, flight_id, golfer_data", [(None, 1, []), ("Test Team Name", 1, None)]
)
def test_create_team_flight_incomplete(
    client: TestClient, name: str, flight_id: int, golfer_data: list
):
    response = client.post(
        "/teams/",
        json={"name": name, "flight_id": flight_id, "golfer_data": golfer_data},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "name, flight_id, golfer_data",
    [
        ({"key": "value"}, 1, []),
        ("Test Team Name", {"key": "value"}, []),
        ("Test Team Name", 1, {"key": "value"}),
    ],
)
def test_create_team_flight_invalid(
    client: TestClient, name: str, flight_id: int, golfer_data: list
):
    response = client.post(
        "/teams/",
        json={"name": name, "flight_id": flight_id, "golfer_data": golfer_data},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_teams(session: Session, client: TestClient):
    golfers = [
        Golfer(name="Test Golfer 1", id=1),
        Golfer(name="Test Golfer 2", id=2),
        Golfer(name="Test Golfer 3", id=3),
    ]
    for golfer in golfers:
        session.add(golfer)

    session.add(Flight(name="Test Flight", year=2021, id=1))

    teams = [
        Team(name="Test Team 1", flight_id=1, id=1),
        Team(name="Test Team 2", flight_id=1, id=2),
    ]
    for team in teams:
        session.add(team)

    session.add(
        TeamGolferLink(team_id=1, golfer_id=1, division_id=1, role=TeamRole.CAPTAIN)
    )
    session.add(
        TeamGolferLink(team_id=2, golfer_id=2, division_id=1, role=TeamRole.CAPTAIN)
    )
    session.add(
        TeamGolferLink(team_id=2, golfer_id=3, division_id=1, role=TeamRole.PLAYER)
    )

    session.commit()

    response = client.get("/teams/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == len(teams)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == teams[dIdx].name
        assert data[dIdx]["id"] == teams[dIdx].id


def test_read_team_flight(session: Session, client: TestClient):
    golfers = [
        Golfer(name="Test Golfer 1", id=1),
        Golfer(name="Test Golfer 2", id=2),
        Golfer(name="Test Golfer 3", id=3),
    ]
    for golfer in golfers:
        session.add(golfer)

    session.add(Flight(name="Test Flight", year=2021, id=1))
    session.add(Division(name="Test Division", gender=TeeGender.MENS, id=1))
    session.add(FlightDivisionLink(flight_id=1, division_id=1))

    team = Team(name="Test Team 1", flight_id=1, id=1)
    session.add(team)

    session.add(
        TeamGolferLink(team_id=1, golfer_id=1, division_id=1, role=TeamRole.CAPTAIN)
    )
    session.add(
        TeamGolferLink(team_id=1, golfer_id=2, division_id=1, role=TeamRole.PLAYER)
    )
    session.add(
        TeamGolferLink(team_id=1, golfer_id=3, division_id=1, role=TeamRole.SUBSTITUTE)
    )

    session.commit()

    response = client.get(f"/teams/{team.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == team.name
    assert data["id"] == team.id


def test_delete_team(session: Session, client: TestClient):
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    team = Team(name="Test Team 1", flight_id=1)
    session.add(team)
    session.commit()

    response = client.delete(f"/teams/{team.id}")
    assert response.status_code == status.HTTP_200_OK

    team_db = session.get(Team, team.id)
    assert team_db is None

    app.dependency_overrides.clear()


def test_delete_team_unauthorized(session: Session, client: TestClient):
    team = Team(name="Test Team 1", flight_id=1)
    session.add(team)
    session.commit()

    response = client.delete(f"/teams/{team.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
