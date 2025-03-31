from sqlmodel import Session, select

from app.models.free_agent import FreeAgent, FreeAgentCreate


def get_free_agent(
    session: Session, flight_id: int, golfer_id: int
) -> FreeAgent | None:
    return session.exec(
        select(FreeAgent)
        .where(FreeAgent.flight_id == flight_id)
        .where(FreeAgent.golfer_id == golfer_id)
    ).one_or_none()


def get_free_agents(session: Session, flight_id: int | None = None) -> list[FreeAgent]:
    query = select(FreeAgent).order_by(FreeAgent.flight_id)
    if flight_id is not None:
        query = query.where(FreeAgent.flight_id == flight_id)
    return list(session.exec(query).all())


def create_free_agent(
    session: Session, new_free_agent: FreeAgentCreate
) -> FreeAgent | None:
    free_agent_db = get_free_agent(
        session=session,
        flight_id=new_free_agent.flight_id,
        golfer_id=new_free_agent.golfer_id,
    )
    if free_agent_db is not None:
        return None
    free_agent_db = FreeAgent.model_validate(new_free_agent)
    session.add(free_agent_db)
    session.commit()
    session.refresh(free_agent_db)
    return free_agent_db


def delete_free_agent(
    session: Session, flight_id: int, golfer_id: int
) -> FreeAgent | None:
    free_agent_db = get_free_agent(
        session=session, flight_id=flight_id, golfer_id=golfer_id
    )
    if free_agent_db is None:
        return None
    session.delete(free_agent_db)
    session.commit()
    return free_agent_db
