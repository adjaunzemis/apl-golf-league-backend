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
from ..models.match import Match
from ..models.match_round_link import MatchRoundLink

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
        Division(name="Test Division 1", gender="M", flight_id=1, home_tee_id=1),
        Division(name="Test Division 2", gender="F", flight_id=2, home_tee_id=2)
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
        assert data[dIdx]["home_tee_id"] == divisions[dIdx].home_tee_id
        assert data[dIdx]["id"] == divisions[dIdx].id

def test_read_division(session: Session, client: TestClient):
    division = Division(name="Test Division 1", gender="M", flight_id=1, home_tee_id=1)
    session.add(division)
    session.commit()

    response = client.get(f"/flights/divisions/{division.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == division.name
    assert data["gender"] == division.gender
    assert data["flight_id"] == division.flight_id
    assert data["home_tee_id"] == division.home_tee_id
    assert data["id"] == division.id

def test_update_division(session: Session, client: TestClient):
    division = Division(name="Test Flight 1", gender="M", flight_id=1, home_tee_id=1)
    session.add(division)
    session.commit()

    response = client.patch(f"/flights/divisions/{division.id}", json={"name": "Awesome Division"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Awesome Division"
    assert data["gender"] == division.gender
    assert data["flight_id"] == division.flight_id
    assert data["home_tee_id"] == division.home_tee_id
    assert data["id"] == division.id

def test_delete_division(session: Session, client: TestClient):
    division = Division(name="Test Flight 1", gender="M", flight_id=1, home_tee_id=1)
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

@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score", [
        (1, 1, 1, 2, 7.5, 3.5),
        (1, 1, 1, 2, 7.5, None),
        (1, 1, 1, 2, None, 3.5),
        (1, 1, 1, 2, None, None),
    ])
def test_create_match(client: TestClient, flight_id: int, week: int, home_team_id: int, away_team_id: int, home_score: float, away_score: float):
    response = client.post("/flights/matches/", json={
        "flight_id": flight_id, "week": week, "home_team_id": home_team_id, "away_team_id": away_team_id, "home_score": home_score, "away_score": away_score
    })
    assert response.status_code == 200
    
    data = response.json()
    assert data["flight_id"] == flight_id
    assert data["week"] == week
    assert data["home_team_id"] == home_team_id
    assert data["away_team_id"] == away_team_id
    assert data["home_score"] == home_score
    assert data["away_score"] == away_score
    assert data["id"] is not None

@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score", [
        (1, None, 1, 2, 7.5, 3.5)
    ])
def test_create_match_incomplete(client: TestClient, flight_id: int, week: int, home_team_id: int, away_team_id: int, home_score: float, away_score: float):
    # Missing required fields
    response = client.post("/flights/matches/", json={
        "flight_id": flight_id, "week": week, "home_team_id": home_team_id, "away_team_id": away_team_id, "home_score": home_score, "away_score": away_score
    })
    assert response.status_code == 422

@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score", [
        ({"key": "value"}, 1, 1, 2, 7.5, 3.5),
        (1, {"key": "value"}, 1, 2, 7.5, 3.5),
        (1, 1, {"key": "value"}, 2, 7.5, 3.5),
        (1, 1, 1, {"key": "value"}, 7.5, 3.5),
        (1, 1, 1, 2, {"key": "value"}, 3.5),
        (1, 1, 1, 2, 7.5, {"key": "value"}),
    ])
def test_create_match_invalid(client: TestClient, flight_id: int, week: int, home_team_id: int, away_team_id: int, home_score: float, away_score: float):
    # Invalid input data types
    response = client.post("/flights/matches/", json={
        "flight_id": flight_id, "week": week, "home_team_id": home_team_id, "away_team_id": away_team_id, "home_score": home_score, "away_score": away_score
    })
    assert response.status_code == 422

def test_read_matches(session: Session, client: TestClient):
    matches = [
        Match(flight_id=1, week=1, home_team_id=1, away_team_id=2),
        Match(flight_id=1, week=2, home_team_id=2, away_team_id=1, home_score=7.5, away_score=3.5)
    ]
    for match in matches:
        session.add(match)
    session.commit()

    response = client.get("/flights/matches/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(matches)
    for dIdx in range(len(data)):
        assert data[dIdx]["flight_id"] == matches[dIdx].flight_id
        assert data[dIdx]["week"] == matches[dIdx].week
        assert data[dIdx]["home_team_id"] == matches[dIdx].home_team_id
        assert data[dIdx]["away_team_id"] == matches[dIdx].away_team_id
        assert data[dIdx]["home_score"] == matches[dIdx].home_score
        assert data[dIdx]["away_score"] == matches[dIdx].away_score
        assert data[dIdx]["id"] == matches[dIdx].id

def test_read_match(session: Session, client: TestClient):
    match = Match(flight_id=1, week=2, home_team_id=2, away_team_id=1, home_score=7.5, away_score=3.5)
    session.add(match)
    session.commit()

    response = client.get(f"/flights/matches/{match.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["flight_id"] == match.flight_id
    assert data["week"] == match.week
    assert data["home_team_id"] == match.home_team_id
    assert data["away_team_id"] == match.away_team_id
    assert data["home_score"] == match.home_score
    assert data["away_score"] == match.away_score
    assert data["id"] == match.id

def test_update_match(session: Session, client: TestClient):
    match = Match(flight_id=1, week=1, home_team_id=1, away_team_id=2)
    session.add(match)
    session.commit()

    response = client.patch(f"/flights/matches/{match.id}", json={"home_score": 7.5, "away_score": 3.5})
    assert response.status_code == 200

    data = response.json()
    assert data["flight_id"] == match.flight_id
    assert data["week"] == match.week
    assert data["home_team_id"] == match.home_team_id
    assert data["away_team_id"] == match.away_team_id
    assert data["home_score"] == 7.5
    assert data["away_score"] == 3.5
    assert data["id"] == match.id

def test_delete_match(session: Session, client: TestClient):
    match = Match(flight_id=1, week=1, home_team_id=1, away_team_id=2)
    session.add(match)
    session.commit()

    response = client.delete(f"/flights/matches/{match.id}")
    assert response.status_code == 200

    match_db = session.get(Match, match.id)
    assert match_db is None

def test_create_match_round_link(client: TestClient):
    match_id = 1
    round_id = 2
    response = client.post(f"/flights/matches/{match_id}/rounds/{round_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["match_id"] == match_id
    assert data["round_id"] == round_id

@pytest.mark.parametrize(
    "match_id, round_id", [
        (None, 2),
        (1, None)
    ])
def test_create_match_round_link_incomplete(client: TestClient, match_id: int, round_id: int):
    # Missing required fields
    response = client.post(f"/flights/matches/{match_id}/rounds/{round_id}")
    assert response.status_code == 422

@pytest.mark.parametrize(
    "match_id, round_id", [
        ({"key": "value"}, 2),
        (1, {"key": "value"})
    ])
def test_create_match_round_link_invalid(client: TestClient, match_id: int, round_id: int):
    # Invalid input data types
    response = client.post(f"/flights/matches/{match_id}/rounds/{round_id}")
    assert response.status_code == 422

def test_read_match_round_links(session: Session, client: TestClient):
    links = [
        MatchRoundLink(match_id=1, round_id=1),
        MatchRoundLink(match_id=1, round_id=2)
    ]
    for link in links:
        session.add(link)
    session.commit()

    response = client.get("/flights/matches/rounds/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(links)
    for dIdx in range(len(data)):
        assert data[dIdx]["match_id"] == links[dIdx].match_id
        assert data[dIdx]["round_id"] == links[dIdx].round_id

def test_read_match_round_links_for_match(session: Session, client: TestClient):
    links = [
        MatchRoundLink(match_id=1, round_id=1),
        MatchRoundLink(match_id=1, round_id=2),
        MatchRoundLink(match_id=2, round_id=3)
    ]
    for link in links:
        session.add(link)
    session.commit()

    match_id = 1
    response = client.get(f"/flights/matches/{match_id}/rounds/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    for dIdx in range(len(data)):
        assert data[dIdx]["match_id"] == links[dIdx].match_id
        assert data[dIdx]["round_id"] == links[dIdx].round_id

def test_delete_match_round_link(session: Session, client: TestClient):
    link = MatchRoundLink(match_id=1, round_id=1)
    session.add(link)
    session.commit()

    response = client.delete(f"/flights/matches/{link.match_id}/rounds/{link.round_id}")
    assert response.status_code == 200

    match_db = session.get(MatchRoundLink, [link.match_id, link.round_id])
    assert match_db is None
