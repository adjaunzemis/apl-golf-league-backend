import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app
from ..dependencies import get_session
from ..models.flight import Flight
from ..models.division import Division
from ..models.team import Team
from ..models.player import Player

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
    "name, year, home_course_id", [
        ("Test Flight Name", 2021, 1),
        ("Test Flight Name", 2021, None)
    ])
def test_create_flight(client: TestClient, name: str, year: int, home_course_id: int):
    response = client.post("/flights/", json={
        "name": name, "year": year, "home_course_id": home_course_id
    })
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == name
    assert data["year"] == year
    assert data["home_course_id"] == home_course_id
    assert data["id"] is not None

@pytest.mark.parametrize(
    "name, year, home_course_id", [
        (None, 2021, 1),
        ("Test Flight Name", None, 1)
    ])
def test_create_flight_incomplete(client: TestClient, name: str, year: int, home_course_id: int):
    # Missing required fields
    response = client.post("/flights/", json={
        "name": name, "year": year, "home_course_id": home_course_id
    })
    assert response.status_code == 422

@pytest.mark.parametrize(
    "name, year, home_course_id", [
        ({"key": "value"}, 2021, 1),
        ("Test Flight Name", {"key": "value"}, 1),
        ("Test Flight Name", 2021, {"key": "value"})
    ])
def test_create_flight_invalid(client: TestClient, name: str, year: int, home_course_id: int):
    # Invalid input data types
    response = client.post("/flights/", json={
        "name": name, "year": year, "home_course_id": home_course_id
    })
    assert response.status_code == 422

def test_read_flights(session: Session, client: TestClient):
    flights = [
        Flight(name="Test Flight 1", year=2021, home_course_id=1),
        Flight(name="Test Flight 2", year=2021, home_course_id=2)
    ]
    for flight in flights:
        session.add(flight)
    session.commit()

    response = client.get("/flights/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(flights)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == flights[dIdx].name
        assert data[dIdx]["year"] == flights[dIdx].year
        assert data[dIdx]["home_course_id"] == flights[dIdx].home_course_id
        assert data[dIdx]["id"] == flights[dIdx].id

def test_read_flight(session: Session, client: TestClient):
    flight = Flight(name="Test Flight 1", year=2021, home_course_id=1)
    session.add(flight)
    session.commit()

    response = client.get(f"/flights/{flight.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == flight.name
    assert data["year"] == flight.year
    assert data["home_course_id"] == flight.home_course_id
    assert data["id"] == flight.id
    assert len(data["divisions"]) == 0
    assert len(data["teams"]) == 0

def test_update_flight(session: Session, client: TestClient):
    flight = Flight(name="Test Flight 1", year=2021, home_course_id=1)
    session.add(flight)
    session.commit()

    response = client.patch(f"/flights/{flight.id}", json={"name": "Awesome Flight"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Awesome Flight"
    assert data["year"] == flight.year
    assert data["home_course_id"] == flight.home_course_id
    assert data["id"] == flight.id

def test_delete_flight(session: Session, client: TestClient):
    flight = Flight(name="Test Flight 1", year=2021, home_course_id=1)
    session.add(flight)
    session.commit()

    response = client.delete(f"/flights/{flight.id}")
    assert response.status_code == 200

    flight_db = session.get(Flight, flight.id)
    assert flight_db is None

@pytest.mark.parametrize(
    "name, gender, flight_id, home_tee_id", [
        ("Test Division Name", "M", 1, 1),
        ("Test Division Name", "F", 1, None),
        ("Test Division Name", "M", None, 1)
    ])
def test_create_division(client: TestClient, name: str, gender: str, flight_id: int, home_tee_id: int):
    response = client.post("/flights/divisions/", json={
        "name": name, "gender": gender, "flight_id": flight_id, "home_tee_id": home_tee_id
    })
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == name
    assert data["gender"] == gender
    assert data["flight_id"] == flight_id
    assert data["home_tee_id"] == home_tee_id
    assert data["id"] is not None

@pytest.mark.parametrize(
    "name, gender, flight_id, home_tee_id", [
        (None, "M", 1, 1),
        ("Test Division Name", None, 1, 1)
    ])
def test_create_division_incomplete(client: TestClient, name: str, gender: str, flight_id: int, home_tee_id: int):
    # Missing required fields
    response = client.post("/flights/divisions/", json={
        "name": name, "gender": gender, "flight_id": flight_id, "home_tee_id": home_tee_id
    })
    assert response.status_code == 422

@pytest.mark.parametrize(
    "name, gender, flight_id, home_tee_id", [
        ("Test Division Name", "INVALID", 1, 1),
        ({"key": "value"}, "M", 1, 1),
        ("Test Division Name", {"key": "value"}, 1, 1),
        ("Test Division Name", "M", {"key": "value"}, 1),
        ("Test Division Name", "M", 1, {"key": "value"})
    ])
def test_create_division_invalid(client: TestClient, name: str, gender: str, flight_id: int, home_tee_id: int):
    # Invalid input data types
    response = client.post("/flights/divisions/", json={
        "name": name, "gender": gender, "flight_id": flight_id, "home_tee_id": home_tee_id
    })
    assert response.status_code == 422

def test_read_divisions(session: Session, client: TestClient):
    divisions = [
        Division(name="Test Division 1", gender="M", flight_id=1, primary_tee_id=1),
        Division(name="Test Division 2", gender="F", flight_id=2, primary_tee_id=2)
    ]
    for division in divisions:
        session.add(division)
    session.commit()

    response = client.get("/flights/divisions/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(divisions)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == divisions[dIdx].name
        assert data[dIdx]["gender"] == divisions[dIdx].gender
        assert data[dIdx]["flight_id"] == divisions[dIdx].flight_id
        assert data[dIdx]["home_tee_id"] == divisions[dIdx].primary_tee_id
        assert data[dIdx]["id"] == divisions[dIdx].id

def test_read_division(session: Session, client: TestClient):
    division = Division(name="Test Division 1", gender="M", flight_id=1, primary_tee_id=1)
    session.add(division)
    session.commit()

    response = client.get(f"/flights/divisions/{division.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == division.name
    assert data["gender"] == division.gender
    assert data["flight_id"] == division.flight_id
    assert data["home_tee_id"] == division.primary_tee_id
    assert data["id"] == division.id

def test_update_division(session: Session, client: TestClient):
    division = Division(name="Test Flight 1", gender="M", flight_id=1, primary_tee_id=1)
    session.add(division)
    session.commit()

    response = client.patch(f"/flights/divisions/{division.id}", json={"name": "Awesome Division"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Awesome Division"
    assert data["gender"] == division.gender
    assert data["flight_id"] == division.flight_id
    assert data["home_tee_id"] == division.primary_tee_id
    assert data["id"] == division.id

def test_delete_division(session: Session, client: TestClient):
    division = Division(name="Test Flight 1", gender="M", flight_id=1, primary_tee_id=1)
    session.add(division)
    session.commit()

    response = client.delete(f"/flights/divisions/{division.id}")
    assert response.status_code == 200

    division_db = session.get(Division, division.id)
    assert division_db is None

@pytest.mark.parametrize(
    "name, flight_id", [
        ("Test Team Name", 1),
        ("Test Team Name", None)
    ])
def test_create_team(client: TestClient, name: str, flight_id: int):
    response = client.post("/flights/teams/", json={
        "name": name, "flight_id": flight_id
    })
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == name
    assert data["flight_id"] == flight_id
    assert data["id"] is not None

@pytest.mark.parametrize(
    "name, flight_id", [
        (None, 1)
    ])
def test_create_team_incomplete(client: TestClient, name: str, flight_id: int):
    # Missing required fields
    response = client.post("/flights/teams/", json={
        "name": name, "flight_id": flight_id
    })
    assert response.status_code == 422

@pytest.mark.parametrize(
    "name, flight_id", [
        ({"key": "value"}, 1),
        ("Test Team Name", {"key": "value"})
    ])
def test_create_team_invalid(client: TestClient, name: str, flight_id: int):
    # Invalid input data types
    response = client.post("/flights/teams/", json={
        "name": name, "flight_id": flight_id
    })
    assert response.status_code == 422

def test_read_teams(session: Session, client: TestClient):
    teams = [
        Team(name="Test Division 1", flight_id=1),
        Team(name="Test Division 2", flight_id=2)
    ]
    for team in teams:
        session.add(team)
    session.commit()

    response = client.get("/flights/teams/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(teams)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == teams[dIdx].name
        assert data[dIdx]["flight_id"] == teams[dIdx].flight_id
        assert data[dIdx]["id"] == teams[dIdx].id

def test_read_team(session: Session, client: TestClient):
    team = Team(name="Test Division 1", flight_id=1)
    session.add(team)
    session.commit()

    response = client.get(f"/flights/teams/{team.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == team.name
    assert data["flight_id"] == team.flight_id
    assert data["id"] == team.id
    assert len(data["players"]) == 0

def test_update_team(session: Session, client: TestClient):
    team = Team(name="Test Division 1", flight_id=1)
    session.add(team)
    session.commit()

    response = client.patch(f"/flights/teams/{team.id}", json={"name": "Awesome Team"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Awesome Team"
    assert data["flight_id"] == team.flight_id
    assert data["id"] == team.id

def test_delete_team(session: Session, client: TestClient):
    team = Team(name="Test Division 1", flight_id=1)
    session.add(team)
    session.commit()

    response = client.delete(f"/flights/teams/{team.id}")
    assert response.status_code == 200

    team_db = session.get(Team, team.id)
    assert team_db is None

@pytest.mark.parametrize(
    "team_id, golfer_id, division_id, role", [
        (1, 2, 3, "CAPTAIN"),
        (1, 2, 3, None),
        (1, 2, None, "PLAYER"),
        (1, None, 3, "SUBSTITUTE"),
        (None, 2, 3, "CAPTAIN")
    ])
def test_create_player(client: TestClient, team_id: int, golfer_id: int, division_id: int, role: str):
    response = client.post("/flights/players/", json={
        "team_id": team_id, "golfer_id": golfer_id, "division_id": division_id, "role": role
    })
    assert response.status_code == 200
    
    data = response.json()
    assert data["team_id"] == team_id
    assert data["golfer_id"] == golfer_id
    assert data["division_id"] == division_id
    assert data["role"] == role
    assert data["id"] is not None

@pytest.mark.parametrize(
    "team_id, golfer_id, division_id, role", [
        (1, 2, 3, "INVALID"),
        (1, 2, 3, {"key": "value"}),
        (1, 2, {"key": "value"}, "CAPTAIN"),
        (1, {"key": "value"}, 3, "CAPTAIN"),
        ({"key": "value"}, 2, 3, "CAPTAIN")
    ])
def test_create_player_invalid(client: TestClient, team_id: int, golfer_id: int, division_id: int, role: str):
    # Invalid input data types
    response = client.post("/flights/players/", json={
        "team_id": team_id, "golfer_id": golfer_id, "division_id": division_id, "role": role
    })
    assert response.status_code == 422

def test_read_players(session: Session, client: TestClient):
    players = [
        Player(team_id=1, golfer_id=1, division_id=1, role="CAPTAIN"),
        Player(team_id=2, golfer_id=2, division_id=2, role="PLAYER")
    ]
    for player in players:
        session.add(player)
    session.commit()

    response = client.get("/flights/players/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(players)
    for dIdx in range(len(data)):
        assert data[dIdx]["team_id"] == players[dIdx].team_id
        assert data[dIdx]["golfer_id"] == players[dIdx].golfer_id
        assert data[dIdx]["division_id"] == players[dIdx].division_id
        assert data[dIdx]["role"] == players[dIdx].role
        assert data[dIdx]["id"] == players[dIdx].id

def test_read_player(session: Session, client: TestClient):
    player = Player(team_id=1, golfer_id=1, division_id=1, role="CAPTAIN")
    session.add(player)
    session.commit()

    response = client.get(f"/flights/players/{player.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["team_id"] == player.team_id
    assert data["golfer_id"] == player.golfer_id
    assert data["division_id"] == player.division_id
    assert data["role"] == player.role
    assert data["id"] == player.id

def test_update_player(session: Session, client: TestClient):
    player = Player(team_id=1, golfer_id=1, division_id=1, role="CAPTAIN")
    session.add(player)
    session.commit()

    response = client.patch(f"/flights/players/{player.id}", json={"role": "SUBSTITUTE"})
    assert response.status_code == 200

    data = response.json()
    assert data["team_id"] == player.team_id
    assert data["golfer_id"] == player.golfer_id
    assert data["division_id"] == player.division_id
    assert data["role"] == "SUBSTITUTE"
    assert data["id"] == player.id

def test_delete_player(session: Session, client: TestClient):
    player = Player(team_id=1, golfer_id=1, division_id=1, role="CAPTAIN")
    session.add(player)
    session.commit()

    response = client.delete(f"/flights/players/{player.id}")
    assert response.status_code == 200

    player_db = session.get(Player, player.id)
    assert player_db is None
