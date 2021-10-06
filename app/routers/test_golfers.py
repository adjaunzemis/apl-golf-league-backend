import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app
from ..dependencies import get_session
from ..models.golfer import Golfer

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    
@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.mark.parametrize(
    "name, affiliation", [
        ("Test Golfer", "Test Affiliation"),
        ("Test Golfer", None),
    ])
def test_create_golfer(client: TestClient, name: str, affiliation: str):
    response = client.post("/golfers/", json={
        "name": name, "affiliation": affiliation
    })
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == name
    assert data["affiliation"] == affiliation
    assert data["id"] is not None

def test_create_golfer_incomplete(client: TestClient):
    # Missing required fields
    response = client.post("/golfers/", json={"affiliation": "Test Affiliation"})
    assert response.status_code == 422

@pytest.mark.parametrize(
    "name, affiliation", [
        ({"key": "value"}, "Test Affiliation"),
        ("Test Golfer", {"key": "value"}),
    ])
def test_create_golfer_invalid(client: TestClient, name: str, affiliation: str):
    response = client.post("/golfers/", json={
        "name": name, "affiliation": affiliation
    })
    assert response.status_code == 422

def test_read_golfers(session: Session, client: TestClient):
    golfers = [
        Golfer(name="Test Golfer A", affiliation="Test Affiliation"),
        Golfer(name="Test Golfer B", affiliation="Other Affiliation")
    ]
    for golfer in golfers:
        session.add(golfer)
    session.commit()

    response = client.get("/golfers/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(golfers)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == golfers[dIdx].name
        assert data[dIdx]["affiliation"] == golfers[dIdx].affiliation
        assert data[dIdx]["id"] == golfers[dIdx].id

def test_read_golfer(session: Session, client: TestClient):
    golfer = Golfer(name="Test Golfer A", affiliation="Test Affiliation")
    session.add(golfer)
    session.commit()

    response = client.get(f"/golfers/{golfer.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == golfer.name
    assert data["affiliation"] == golfer.affiliation
    assert data["id"] == golfer.id

def test_update_golfer(session: Session, client: TestClient):
    golfer = Golfer(name="Test Golfer A", affiliation="Test Affiliation")
    session.add(golfer)
    session.commit()

    response = client.patch(f"/golfers/{golfer.id}", json={"name": "New Golfer"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "New Golfer"
    assert data["affiliation"] == golfer.affiliation
    assert data["id"] == golfer.id

def test_delete_golfer(session: Session, client: TestClient):
    golfer = Golfer(name="Test Golfer A", affiliation="Test Affiliation")
    session.add(golfer)
    session.commit()

    response = client.delete(f"/golfers/{golfer.id}")
    assert response.status_code == 200

    golfer_db = session.get(Golfer, golfer.id)
    assert golfer_db is None
