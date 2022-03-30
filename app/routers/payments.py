from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_session
from ..models.payment import LeagueDuesPayment, LeagueDuesPaymentRead, LeagueDuesPaymentUpdate
from ..models.user import User
from ..models.golfer import Golfer

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

class LeagueDuesPaymentInfo(LeagueDuesPaymentRead):
    golfer_name: str

@router.get("/", response_model=List[LeagueDuesPaymentInfo])
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

@router.patch("/{payment_id}", response_model=LeagueDuesPaymentRead)
async def update_league_dues_payment(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), payment_id: int, payment: LeagueDuesPaymentUpdate):
    # TODO: Validate current user privileges
    payment_db = session.get(LeagueDuesPayment, payment_id)
    if not payment_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment_data = payment.dict(exclude_unset=True)
    for key, value in payment_data.items():
        setattr(payment_db, key, value)
    session.add(payment_db)
    session.commit()
    session.refresh(payment_db)
    return payment_db
