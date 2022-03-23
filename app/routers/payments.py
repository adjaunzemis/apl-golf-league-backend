from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_session
from ..models.payment import LeagueDuesPayment, LeagueDuesPaymentRead
from ..models.user import User

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

@router.get("/", response_model=List[LeagueDuesPaymentRead])
async def read_payments_for_year(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), year: int):
    # TODO: Validate current user privileges
    return session.exec(select(LeagueDuesPayment).where(LeagueDuesPayment.year == year)).all()
