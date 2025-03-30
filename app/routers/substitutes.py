from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session

from app.database import substitutes as db_substitutes
from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.substitutes import Substitute, SubstituteCreate
from app.models.user import User

router = APIRouter(prefix="/substitutes", tags=["Substitutes"])


@router.get("/", response_model=list[Substitute])
async def get_substitutes(
    *,
    session: Session = Depends(get_sql_db_session),
):
    return db_substitutes.get_substitutes(session)


@router.get("/{year}", response_model=Substitute)
async def get_substitute_for_flight(
    *,
    session: Session = Depends(get_sql_db_session),
    flight_id: int = Path(..., description="Flight identifier"),
):
    return db_substitutes.get_substitutes(session, flight_id)


@router.post("/", response_model=Substitute)
async def create_substitute(
    *,
    session: Session = Depends(get_sql_db_session),
    new_substitute: SubstituteCreate = Body(..., description="New substitute to add"),
):
    substitute_db = db_substitutes.create_substitute(session, new_substitute)
    if substitute_db is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unable to create substitute",
        )
    return substitute_db


@router.delete("/")
async def delete_substitute(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    flight_id: int = Query(..., description="Flight identifier"),
    golfer_id: int = Query(..., description="Golfer identifier"),
) -> Substitute | None:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Insufficient privileges to delete substitute",
        )
    substitute_db = db_substitutes.delete_substitute(session, flight_id, golfer_id)
    if substitute_db is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to delete substitute",
        )
    return substitute_db
