from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session, SQLModel, select

from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.golfer import Golfer
from app.models.payment import (
    LeagueDues,
    LeagueDuesPayment,
    LeagueDuesPaymentRead,
    LeagueDuesPaymentUpdate,
    LeagueDuesRead,
    LeagueDuesType,
    PaymentMethod,
    TournamentEntryFeePayment,
    TournamentEntryFeePaymentRead,
    TournamentEntryFeePaymentUpdate,
    TournamentEntryFeeType,
)
from app.models.tournament import Tournament
from app.models.user import User

router = APIRouter(prefix="/payments", tags=["Payments"])


class LeagueDuesPaymentData(LeagueDuesPaymentRead):
    golfer_name: str
    golfer_email: Optional[str]


class LeagueDuesPaymentInfo(SQLModel):
    id: int
    golfer_id: int
    golfer_name: str
    year: int
    type: LeagueDuesType
    amount_due: float
    amount_paid: float
    is_paid: bool


class LeagueDuesPaypalTransactionItem(SQLModel):
    id: Optional[int] = None
    golfer_id: int
    type: LeagueDuesType


class LeagueDuesPaypalTransaction(SQLModel):
    year: int
    amount: float
    description: str
    items: List[LeagueDuesPaypalTransactionItem]
    resource_id: Optional[str] = None
    update_time: Optional[str] = None
    payer_name: Optional[str] = None
    payer_email: Optional[str] = None


class TournamentEntryFeePaymentData(TournamentEntryFeePaymentRead):
    golfer_name: str
    golfer_email: Optional[str]


class TournamentEntryFeePaymentInfo(SQLModel):
    id: int
    golfer_id: int
    golfer_name: str
    year: int
    tournament_id: int
    type: TournamentEntryFeeType
    amount_due: float
    amount_paid: float
    is_paid: bool


class TournamentEntryFeePaypalTransactionItem(SQLModel):
    id: Optional[int] = None
    golfer_id: int
    type: TournamentEntryFeeType


class TournamentEntryFeePaypalTransaction(SQLModel):
    year: int
    tournament_id: int
    amount: float
    description: str
    items: List[TournamentEntryFeePaypalTransactionItem]
    resource_id: Optional[str] = None
    update_time: Optional[str] = None
    payer_name: Optional[str] = None
    payer_email: Optional[str] = None


@router.get("/dues/amounts", response_model=List[LeagueDuesRead])
async def read_league_dues_amounts_for_year(
    *, session: Session = Depends(get_sql_db_session), year: int
):
    return session.exec(select(LeagueDues).where(LeagueDues.year == year)).all()


@router.get("/dues/info", response_model=List[LeagueDuesPaymentInfo])
async def read_league_dues_payment_info_for_year(
    *, session: Session = Depends(get_sql_db_session), year: int
):
    payment_query_data = session.exec(
        select(LeagueDuesPayment, Golfer)
        .join(Golfer, onclause=Golfer.id == LeagueDuesPayment.golfer_id)
        .where(LeagueDuesPayment.year == year)
    ).all()
    return [
        LeagueDuesPaymentInfo(
            id=payment_db.id,
            golfer_id=payment_db.golfer_id,
            golfer_name=golfer_db.name,
            year=payment_db.year,
            type=payment_db.type,
            amount_due=payment_db.amount_due,
            amount_paid=payment_db.amount_paid,
            is_paid=payment_db.is_paid,
        )
        for payment_db, golfer_db in payment_query_data
    ]


@router.get("/dues/data", response_model=List[LeagueDuesPaymentData])
async def read_league_dues_payment_data_for_year(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    year: int,
):
    if not current_user.edit_payments:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to view payments",
        )
    payment_query_data = session.exec(
        select(LeagueDuesPayment, Golfer)
        .join(Golfer, onclause=Golfer.id == LeagueDuesPayment.golfer_id)
        .where(LeagueDuesPayment.year == year)
    ).all()
    return [
        LeagueDuesPaymentData(
            id=payment_db.id,
            golfer_id=payment_db.golfer_id,
            golfer_name=golfer_db.name,
            golfer_email=golfer_db.email,
            year=payment_db.year,
            type=payment_db.type,
            amount_due=payment_db.amount_due,
            amount_paid=payment_db.amount_paid,
            is_paid=payment_db.is_paid,
            linked_payment_id=payment_db.linked_payment_id,
            method=payment_db.method,
            comment=payment_db.comment,
        )
        for payment_db, golfer_db in payment_query_data
    ]


@router.post("/dues")
async def post_league_dues_paypal_transaction(
    *,
    session: Session = Depends(get_sql_db_session),
    transaction: LeagueDuesPaypalTransaction = Body(...),
):
    try:
        first_item_payment_id = None
        for item in transaction.items:
            payment_db = None
            if item.id is not None:
                payment_db = session.get(LeagueDuesPayment, item.id)

            if not payment_db:  # create new payment entry in database
                dues_amount = session.exec(
                    select(LeagueDues.amount)
                    .where(LeagueDues.year == transaction.year)
                    .where(LeagueDues.type == item.type)
                ).one()

                payment_db = LeagueDuesPayment(
                    golfer_id=item.golfer_id,
                    year=transaction.year,
                    type=item.type,
                    amount_due=dues_amount,
                )
                session.add(payment_db)
                session.commit()
                session.refresh(payment_db)

            # Update payment entry
            setattr(
                payment_db, "amount_paid", payment_db.amount_due
            )  # TODO: validate from transaction
            setattr(payment_db, "is_paid", True)  # TODO: validate from transaction
            setattr(payment_db, "method", PaymentMethod.PAYPAL)

            if first_item_payment_id is not None:
                setattr(payment_db, "linked_payment_id", first_item_payment_id)

            payment_comment = f"{transaction.description} | {transaction.resource_id} | {transaction.update_time} | {transaction.payer_name} | {transaction.payer_email}"
            setattr(payment_db, "comment", payment_comment)

            session.add(payment_db)
            session.commit()
            session.refresh(payment_db)

            # Cache first payment id of group of items
            if first_item_payment_id is None:
                first_item_payment_id = payment_db.id
    except:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Unexpected error processing PayPal transaction - please contact treasurer or webmaster!",
        )


@router.patch("/dues/{payment_id}", response_model=LeagueDuesPaymentRead)
async def update_league_dues_payment(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    payment_id: int,
    payment: LeagueDuesPaymentUpdate,
):
    if not current_user.edit_payments:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to update payments",
        )
    payment_db = session.get(LeagueDuesPayment, payment_id)
    if not payment_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment_data = payment.model_dump(exclude_unset=True)
    for key, value in payment_data.items():
        setattr(payment_db, key, value)
    session.add(payment_db)
    session.commit()
    session.refresh(payment_db)
    return payment_db


@router.get(
    "/fees/info/{tournament_id}", response_model=List[TournamentEntryFeePaymentInfo]
)
async def read_tournament_entry_fees_payment_info(
    *, session: Session = Depends(get_sql_db_session), tournament_id: int
):
    payment_query_data = session.exec(
        select(TournamentEntryFeePayment, Golfer)
        .join(Golfer, onclause=Golfer.id == TournamentEntryFeePayment.golfer_id)
        .where(TournamentEntryFeePayment.tournament_id == tournament_id)
    ).all()
    return [
        TournamentEntryFeePaymentInfo(
            id=payment_db.id,
            golfer_id=payment_db.golfer_id,
            golfer_name=golfer_db.name,
            year=payment_db.year,
            tournament_id=payment_db.tournament_id,
            type=payment_db.type,
            amount_due=payment_db.amount_due,
            amount_paid=payment_db.amount_paid,
            is_paid=payment_db.is_paid,
        )
        for payment_db, golfer_db in payment_query_data
    ]


@router.get(
    "/fees/data/{tournament_id}", response_model=List[TournamentEntryFeePaymentData]
)
async def read_tournament_entry_fee_payment_data(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    tournament_id: int,
):
    if not current_user.edit_payments:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to view payments",
        )
    payment_query_data = session.exec(
        select(TournamentEntryFeePayment, Golfer)
        .join(Golfer, onclause=Golfer.id == TournamentEntryFeePayment.golfer_id)
        .where(TournamentEntryFeePayment.tournament_id == tournament_id)
    ).all()
    return [
        TournamentEntryFeePaymentData(
            id=payment_db.id,
            golfer_id=payment_db.golfer_id,
            golfer_name=golfer_db.name,
            golfer_email=golfer_db.email,
            year=payment_db.year,
            tournament_id=payment_db.tournament_id,
            type=payment_db.type,
            amount_due=payment_db.amount_due,
            amount_paid=payment_db.amount_paid,
            is_paid=payment_db.is_paid,
            linked_payment_id=payment_db.linked_payment_id,
            method=payment_db.method,
            comment=payment_db.comment,
        )
        for payment_db, golfer_db in payment_query_data
    ]


@router.post("/fees")
async def post_tournament_entry_fee_paypal_transaction(
    *,
    session: Session = Depends(get_sql_db_session),
    transaction: TournamentEntryFeePaypalTransaction = Body(...),
):
    try:
        first_item_payment_id = None
        for item in transaction.items:
            payment_db = None
            if item.id is not None:
                payment_db = session.get(TournamentEntryFeePayment, item.id)

            if not payment_db:  # create new payment entry in database
                tournament_db = session.exec(
                    select(Tournament).where(Tournament.id == transaction.tournament_id)
                ).one()

                if item.type == TournamentEntryFeeType.MEMBER_FEE:
                    entry_fee = tournament_db.members_entry_fee
                else:
                    entry_fee = tournament_db.non_members_entry_fee

                payment_db = TournamentEntryFeePayment(
                    golfer_id=item.golfer_id,
                    year=transaction.year,
                    tournament_id=transaction.tournament_id,
                    type=item.type,
                    amount_due=entry_fee,
                )
                session.add(payment_db)
                session.commit()
                session.refresh(payment_db)

            # Update payment entry
            setattr(
                payment_db, "amount_paid", payment_db.amount_due
            )  # TODO: validate from transaction
            setattr(payment_db, "is_paid", True)  # TODO: validate from transaction
            setattr(payment_db, "method", PaymentMethod.PAYPAL)

            if first_item_payment_id is not None:
                setattr(payment_db, "linked_payment_id", first_item_payment_id)

            payment_comment = f"{transaction.description} | {transaction.resource_id} | {transaction.update_time} | {transaction.payer_name} | {transaction.payer_email}"
            setattr(payment_db, "comment", payment_comment)

            session.add(payment_db)
            session.commit()
            session.refresh(payment_db)

            # Cache first payment id of group of items
            if first_item_payment_id is None:
                first_item_payment_id = payment_db.id
    except:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Unexpected error processing PayPal transaction - please contact treasurer or webmaster!",
        )


@router.patch("/fees/{payment_id}", response_model=TournamentEntryFeePaymentRead)
async def update_tournament_entry_fee_payment(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    payment_id: int,
    payment: TournamentEntryFeePaymentUpdate,
):
    if not current_user.edit_payments:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to update payments",
        )
    payment_db = session.get(TournamentEntryFeePayment, payment_id)
    if not payment_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment_data = payment.model_dump(exclude_unset=True)
    for key, value in payment_data.items():
        setattr(payment_db, key, value)
    session.add(payment_db)
    session.commit()
    session.refresh(payment_db)
    return payment_db
