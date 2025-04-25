from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session

from app.database import free_agents as db_free_agents
from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.flight import FlightFreeAgent, FlightFreeAgentCreate
from app.models.tournament import TournamentFreeAgent, TournamentFreeAgentCreate
from app.models.user import User

router = APIRouter(prefix="/free-agents", tags=["Free Agents"])


@router.get("/flight/", response_model=list[FlightFreeAgent])
async def get_flight_free_agents(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int | None = Query(None, description="Flight identifier"),
):
    return db_free_agents.get_flight_free_agents(session, flight_id=flight_id)


@router.post("/flight/", response_model=FlightFreeAgent)
async def create_flight_free_agent(
    *,
    session: Session = Depends(get_sql_db_session),
    new_free_agent: FlightFreeAgentCreate = Body(
        ..., description="New free agent to add"
    ),
):
    free_agent_db = db_free_agents.create_flight_free_agent(
        session, new_free_agent=new_free_agent
    )
    if free_agent_db is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Unable to create free agent",
        )
    return free_agent_db


@router.delete("/flight/")
async def delete_flight_free_agent(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight_id: int = Query(..., description="Flight identifier"),
    golfer_id: int = Query(..., description="Golfer identifier"),
) -> FlightFreeAgent | None:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient privileges to delete free agent",
        )
    free_agent_db = db_free_agents.delete_flight_free_agent(
        session, flight_id=flight_id, golfer_id=golfer_id
    )
    if free_agent_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to delete free agent",
        )
    return free_agent_db


@router.get("/tournament/", response_model=list[TournamentFreeAgent])
async def get_tournament_free_agents(
    *,
    session: Session = Depends(get_sql_db_session),
    tournament_id: int | None = Query(None, description="Tournament identifier"),
):
    return db_free_agents.get_tournament_free_agents(
        session, tournament_id=tournament_id
    )


@router.post("/tournament/", response_model=TournamentFreeAgent)
async def create_tournament_free_agent(
    *,
    session: Session = Depends(get_sql_db_session),
    new_free_agent: TournamentFreeAgentCreate = Body(
        ..., description="New free agent to add"
    ),
):
    free_agent_db = db_free_agents.create_tournament_free_agent(
        session, new_free_agent=new_free_agent
    )
    if free_agent_db is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Unable to create free agent",
        )
    return free_agent_db


@router.delete("/tournament/")
async def delete_tournament_free_agent(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    tournament_id: int = Query(..., description="Tournament identifier"),
    golfer_id: int = Query(..., description="Golfer identifier"),
) -> TournamentFreeAgent | None:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient privileges to delete free agent",
        )
    free_agent_db = db_free_agents.delete_tournament_free_agent(
        session, tournament_id=tournament_id, golfer_id=golfer_id
    )
    if free_agent_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to delete free agent",
        )
    return free_agent_db
