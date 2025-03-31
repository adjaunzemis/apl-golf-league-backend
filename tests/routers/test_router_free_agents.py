import pytest
from fastapi import status
from sqlmodel import Session

from app.models.free_agent import FreeAgent


@pytest.fixture()
def session_with_free_agents(session: Session):
    session.add(FreeAgent(flight_id=1, golfer_id=1, division_id=1))
    session.add(FreeAgent(flight_id=1, golfer_id=2, division_id=1))
    session.add(FreeAgent(flight_id=2, golfer_id=3, division_id=1))
    session.commit()
    yield session


def test_get_free_agents(session_with_free_agents, client_unauthorized):
    response = client_unauthorized.get("/free_agents/")
    assert response.status_code == status.HTTP_200_OK
    free_agents_api = [
        FreeAgent(**free_agent_json) for free_agent_json in response.json()
    ]
    assert len(free_agents_api) == 3


def test_get_free_agents_for_flight(session_with_free_agents, client_unauthorized):
    response = client_unauthorized.get("/free_agents/?flight_id=1")
    assert response.status_code == status.HTTP_200_OK
    free_agents_api = [
        FreeAgent(**free_agent_json) for free_agent_json in response.json()
    ]
    assert len(free_agents_api) == 2
    for free_agent_api in free_agents_api:
        assert free_agent_api.flight_id == 1


def test_get_free_agents_for_flight_empty(
    session_with_free_agents, client_unauthorized
):
    response = client_unauthorized.get("/free_agents/?flight_id=3")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


def test_create_free_agent(session_with_free_agents, client_unauthorized):
    response = client_unauthorized.post(
        "/free_agents/", json={"flight_id": 1, "golfer_id": 5, "division_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    free_agent_api = FreeAgent(**response.json())
    assert free_agent_api.flight_id == 1
    assert free_agent_api.golfer_id == 5
    assert free_agent_api.division_id == 1


def test_create_free_agent_duplicate(session_with_free_agents, client_admin):
    response = client_admin.post(
        "/free_agents/", json={"flight_id": 1, "golfer_id": 1, "division_id": 1}
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_free_agent_unauthorized(session_with_free_agents, client_unauthorized):
    response = client_unauthorized.delete("/free_agents/?flight_id=1&golfer_id=2")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_free_agent_non_admin(session_with_free_agents, client_non_admin):
    response = client_non_admin.delete("/free_agents/?flight_id=1&golfer_id=2")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_free_agent(session_with_free_agents, client_admin):
    response = client_admin.delete("/free_agents/?flight_id=1&golfer_id=2")
    assert response.status_code == status.HTTP_200_OK
    active_free_agent_api = FreeAgent(**response.json())
    assert active_free_agent_api.flight_id == 1
    assert active_free_agent_api.golfer_id == 2


def test_delete_free_agent_not_found(session_with_free_agents, client_admin):
    response = client_admin.delete("/free_agents/?flight_id=1&golfer_id=5")
    assert response.status_code == status.HTTP_404_NOT_FOUND
