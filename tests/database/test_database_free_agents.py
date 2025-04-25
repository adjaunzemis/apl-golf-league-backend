import pytest
from sqlmodel import Session

from app.database import free_agents as db_free_agents
from app.models.flight import (
    FlightFreeAgent,
    FlightFreeAgentCadence,
    FlightFreeAgentCreate,
)


@pytest.fixture()
def session_with_free_agents(session: Session):
    session.add(
        FlightFreeAgent(
            flight_id=1,
            golfer_id=1,
            division_id=1,
            cadence=FlightFreeAgentCadence.WEEKLY,
        )
    )
    session.add(
        FlightFreeAgent(
            flight_id=1,
            golfer_id=2,
            division_id=1,
            cadence=FlightFreeAgentCadence.BIWEEKLY,
        )
    )
    session.add(
        FlightFreeAgent(
            flight_id=2,
            golfer_id=3,
            division_id=1,
            cadence=FlightFreeAgentCadence.MONTHLY,
        )
    )
    session.commit()
    yield session


def test_get_free_agent(session_with_free_agents):
    free_agent_db = db_free_agents.get_flight_free_agent(
        session_with_free_agents, flight_id=1, golfer_id=1
    )
    assert free_agent_db is not None
    assert free_agent_db.flight_id == 1
    assert free_agent_db.golfer_id == 1


def test_get_free_agent_not_found(session_with_free_agents):
    free_agent_db = db_free_agents.get_flight_free_agent(
        session_with_free_agents, flight_id=1, golfer_id=5
    )
    assert free_agent_db is None


def test_get_free_agents(session_with_free_agents):
    result = db_free_agents.get_flight_free_agents(session_with_free_agents)
    assert len(result) == 3


@pytest.mark.parametrize("flight_id, num_free_agents", [(1, 2), (2, 1), (3, 0)])
def test_get_free_agents_for_flight(
    session_with_free_agents, flight_id, num_free_agents
):
    results = db_free_agents.get_flight_free_agents(
        session_with_free_agents, flight_id=flight_id
    )
    assert len(results) == num_free_agents
    assert len(set([sub.golfer_id for sub in results])) == num_free_agents
    for sub in results:
        assert sub.flight_id == flight_id


def test_create_free_agent(session_with_free_agents):
    new_free_agent = FlightFreeAgentCreate(
        flight_id=1, golfer_id=3, division_id=1, cadence=FlightFreeAgentCadence.WEEKLY
    )
    free_agent_db = db_free_agents.create_flight_free_agent(
        session_with_free_agents, new_free_agent
    )
    assert free_agent_db.flight_id == new_free_agent.flight_id
    assert free_agent_db.golfer_id == new_free_agent.golfer_id


def test_create_free_agent_conflict(session_with_free_agents):
    new_free_agent = FlightFreeAgentCreate(
        flight_id=1, golfer_id=1, division_id=1, cadence=FlightFreeAgentCadence.WEEKLY
    )
    free_agent_db = db_free_agents.create_flight_free_agent(
        session_with_free_agents, new_free_agent
    )
    assert free_agent_db is None


def test_delete_free_agent(session_with_free_agents):
    free_agent_db = db_free_agents.delete_flight_free_agent(
        session_with_free_agents, flight_id=1, golfer_id=1
    )
    assert free_agent_db.flight_id == 1
    assert free_agent_db.golfer_id == 1
    assert (
        db_free_agents.get_flight_free_agent(
            session_with_free_agents, flight_id=1, golfer_id=1
        )
        is None
    )


def test_delete_free_agent_not_found(session_with_free_agents):
    free_agent = db_free_agents.delete_flight_free_agent(
        session_with_free_agents, flight_id=1, golfer_id=5
    )
    assert free_agent is None
