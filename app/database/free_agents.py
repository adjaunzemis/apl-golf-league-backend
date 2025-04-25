from sqlmodel import Session, select

from app.models.flight import FlightFreeAgent, FlightFreeAgentCreate


def get_flight_free_agent(
    session: Session, flight_id: int, golfer_id: int
) -> FlightFreeAgent | None:
    return session.exec(
        select(FlightFreeAgent)
        .where(FlightFreeAgent.flight_id == flight_id)
        .where(FlightFreeAgent.golfer_id == golfer_id)
    ).one_or_none()


def get_flight_free_agents(
    session: Session, flight_id: int | None = None
) -> list[FlightFreeAgent]:
    query = select(FlightFreeAgent).order_by(FlightFreeAgent.flight_id)
    if flight_id is not None:
        query = query.where(FlightFreeAgent.flight_id == flight_id)
    return list(session.exec(query).all())


def create_flight_free_agent(
    session: Session, new_free_agent: FlightFreeAgentCreate
) -> FlightFreeAgent | None:
    free_agent_db = get_flight_free_agent(
        session=session,
        flight_id=new_free_agent.flight_id,
        golfer_id=new_free_agent.golfer_id,
    )
    if free_agent_db is not None:
        return None
    free_agent_db = FlightFreeAgent.model_validate(new_free_agent)
    session.add(free_agent_db)
    session.commit()
    session.refresh(free_agent_db)
    return free_agent_db


def delete_flight_free_agent(
    session: Session, flight_id: int, golfer_id: int
) -> FlightFreeAgent | None:
    free_agent_db = get_flight_free_agent(
        session=session, flight_id=flight_id, golfer_id=golfer_id
    )
    if free_agent_db is None:
        return None
    session.delete(free_agent_db)
    session.commit()
    return free_agent_db
