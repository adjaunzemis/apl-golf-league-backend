from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_session
from ..models.payment import LeagueDuesPayment, LeagueDuesPaymentRead
from ..models.user import User
from ..models.golfer import Golfer

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

class LeagueDuesPaymentInfo(LeagueDuesPaymentRead):
    golfer_name: str

@router.get("/", response_model=List[LeagueDuesPaymentRead])
async def read_league_dues_payments_for_year(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), year: int):
    # TODO: Validate current user privileges
    payment_query_data = session.exec(select(LeagueDuesPayment, Golfer).join(Golfer, onclause=Golfer.id == LeagueDuesPayment.golfer_id).where(LeagueDuesPayment.year == year)).all()
    return [LeagueDuesPaymentInfo(
        id=payment_db.id,
        golfer_id=payment_db.golfer_id,
        golfer_name=golfer_db.name,
        year=payment_db.year,
        type=payment_db.type,
        amount_due=payment_db.amount_due,
        amount_paid=payment_db.amount_paid,
        is_paid=payment_db.is_paid,
        linked_payment_id=payment_db.linked_payment_id,
        method=payment_db.method,
        confirmation=payment_db.confirmation
    ) for payment_db, golfer_db in payment_query_data]
