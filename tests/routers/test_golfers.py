import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api import app
from app.dependencies import get_current_user, get_sql_db_session
from app.models.golfer import Golfer, GolferAffiliation
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
    "name, affiliation",
    [
        ("Test Golfer", GolferAffiliation.APL_EMPLOYEE),
        ("Test Golfer", None),
    ],
)
def test_create_golfer(client: TestClient, name: str, affiliation: str):
    response = client.post("/golfers/", json={"name": name, "affiliation": affiliation})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == name
    assert data["affiliation"] == affiliation
    assert data["id"] is not None


def test_create_golfer_incomplete(client: TestClient):
    response = client.post(
        "/golfers/", json={"affiliation": GolferAffiliation.NON_APL_EMPLOYEE}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "name, affiliation",
    [
        ({"key": "value"}, GolferAffiliation.NON_APL_EMPLOYEE),
        ("Test Golfer", {"key": "value"}),
        ("Test Golfer", "BAD_AFFILIATION"),
    ],
)
def test_create_golfer_invalid(client: TestClient, name: str, affiliation: str):
    response = client.post("/golfers/", json={"name": name, "affiliation": affiliation})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_golfers(session: Session, client: TestClient):
    golfers = [
        Golfer(name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE),
        Golfer(name="Test Golfer B", affiliation=GolferAffiliation.APL_EMPLOYEE),
    ]
    for golfer in golfers:
        session.add(golfer)
    session.commit()

    response = client.get("/golfers/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["num_golfers"] == len(golfers)
    assert len(data["golfers"]) == len(golfers)
    for dIdx in range(len(data["golfers"])):
        assert data["golfers"][dIdx]["name"] == golfers[dIdx].name
        assert data["golfers"][dIdx]["affiliation"] == golfers[dIdx].affiliation
        assert data["golfers"][dIdx]["golfer_id"] == golfers[dIdx].id


def test_read_golfer(session: Session, client: TestClient):
    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client.get(f"/golfers/{golfer.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == golfer.name
    assert data["affiliation"] == golfer.affiliation
    assert data["golfer_id"] == golfer.id


def test_update_golfer(session: Session, client: TestClient):
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client.patch(f"/golfers/{golfer.id}", json={"name": "New Golfer"})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == "New Golfer"
    assert data["affiliation"] == golfer.affiliation
    assert data["id"] == golfer.id

    app.dependency_overrides.clear()


def test_update_golfer_unauthorized(session: Session, client: TestClient):
    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client.patch(f"/golfers/{golfer.id}", json={"name": "New Golfer"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_golfer(session: Session, client: TestClient):
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client.delete(f"/golfers/{golfer.id}")
    assert response.status_code == status.HTTP_200_OK

    golfer_db = session.get(Golfer, golfer.id)
    assert golfer_db is None

    app.dependency_overrides.clear()


def test_delete_golfer_unauthorized(session: Session, client: TestClient):
    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client.delete(f"/golfers/{golfer.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
