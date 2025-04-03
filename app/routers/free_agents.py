from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session

from app.database import free_agents as db_free_agents
from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.free_agent import FreeAgent, FreeAgentCreate
from app.models.user import User

router = APIRouter(prefix="/free-agents", tags=["Free Agents"])


@router.get("/", response_model=list[FreeAgent])
async def get_free_agents(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int | None = Query(None, description="Flight identifier"),
):
    return db_free_agents.get_free_agents(session, flight_id=flight_id)


@router.post("/", response_model=FreeAgent)
async def create_free_agent(
    *,
    session: Session = Depends(get_sql_db_session),
    new_free_agent: FreeAgentCreate = Body(..., description="New free agent to add"),
):
    free_agent_db = db_free_agents.create_free_agent(
        session, new_free_agent=new_free_agent
    )
    if free_agent_db is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Unable to create free agent",
        )
    return free_agent_db


@router.delete("/")
async def delete_free_agent(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight_id: int = Query(..., description="Flight identifier"),
    golfer_id: int = Query(..., description="Golfer identifier"),
) -> FreeAgent | None:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient privileges to delete free agent",
        )
    free_agent_db = db_free_agents.delete_free_agent(
        session, flight_id=flight_id, golfer_id=golfer_id
    )
    if free_agent_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to delete free agent",
        )
    return free_agent_db
