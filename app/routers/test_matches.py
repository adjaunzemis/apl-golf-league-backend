import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app
from ..dependencies import get_sql_db_session
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
    app.dependency_overrides[get_sql_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.mark.parametrize(
    "flight_id, week, home_team_id, away_team_id, home_score, away_score", [
        (1, 1, 1, 2, 7.5, 3.5),
        (1, 1, 1, 2, 7.5, None),
        (1, 1, 1, 2, None, 3.5),
        (1, 1, 1, 2, None, None),
    ])
def test_create_match(client: TestClient, flight_id: int, week: int, home_team_id: int, away_team_id: int, home_score: float, away_score: float):
    response = client.post("/matches/", json={
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
    response = client.post("/matches/", json={
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
    response = client.post("/matches/", json={
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

    response = client.get("/matches/")
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

    response = client.get(f"/matches/{match.id}")
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

    response = client.patch(f"/matches/{match.id}", json={"home_score": 7.5, "away_score": 3.5})
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

    response = client.delete(f"/matches/{match.id}")
    assert response.status_code == 200

    match_db = session.get(Match, match.id)
    assert match_db is None

def test_create_match_round_link(client: TestClient):
    match_id = 1
    round_id = 2
    response = client.post(f"/matches/{match_id}/rounds/{round_id}")
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
    response = client.post(f"/matches/{match_id}/rounds/{round_id}")
    assert response.status_code == 422

@pytest.mark.parametrize(
    "match_id, round_id", [
        ({"key": "value"}, 2),
        (1, {"key": "value"})
    ])
def test_create_match_round_link_invalid(client: TestClient, match_id: int, round_id: int):
    # Invalid input data types
    response = client.post(f"/matches/{match_id}/rounds/{round_id}")
    assert response.status_code == 422

def test_read_match_round_links(session: Session, client: TestClient):
    links = [
        MatchRoundLink(match_id=1, round_id=1),
        MatchRoundLink(match_id=1, round_id=2)
    ]
    for link in links:
        session.add(link)
    session.commit()

    response = client.get("/matches/rounds/")
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
    response = client.get(f"/matches/{match_id}/rounds/")
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

    response = client.delete(f"/matches/{link.match_id}/rounds/{link.round_id}")
    assert response.status_code == 200

    match_db = session.get(MatchRoundLink, [link.match_id, link.round_id])
    assert match_db is None
