from enum import StrEnum
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel


class LeagueDuesType(StrEnum):
    FLIGHT_DUES = "Flight Dues"
    TOURNAMENT_ONLY_DUES = "Tournament-Only Dues"


class TournamentEntryFeeType(StrEnum):
    MEMBER_FEE = "Member Fee"
    NON_MEMBER_FEE = "Non-Member Fee"


class PaymentMethod(StrEnum):
    CASH_OR_CHECK = "Cash or Check"
    PAYPAL = "PayPal"
    EXEMPT = "Exempt"
    LINKED = "Linked"


class LeagueDuesBase(SQLModel):
    year: int
    type: LeagueDuesType = Field(
        sa_column=Column(
            SAEnum(
                LeagueDuesType,
                name="league_dues_type_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=False,
        )
    )
    amount: float


class LeagueDues(LeagueDuesBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class LeagueDuesCreate(LeagueDuesBase):
    pass


class LeagueDuesUpdate(SQLModel):
    year: Optional[int] = None
    type: Optional[LeagueDuesType] = None
    amount: Optional[float] = None


class LeagueDuesRead(LeagueDuesBase):
    id: int


class LeagueDuesPaymentBase(SQLModel):
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    year: int
    type: LeagueDuesType
    amount_due: float
    amount_paid: Optional[float] = 0
    is_paid: Optional[bool] = False
    linked_payment_id: Optional[int] = None
    method: Optional[PaymentMethod] = Field(
        sa_column=Column(
            SAEnum(
                PaymentMethod,
                name="payment_method_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=True,
        )
    )
    comment: Optional[str] = None


class LeagueDuesPayment(LeagueDuesPaymentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class LeagueDuesPaymentCreate(LeagueDuesPaymentBase):
    pass


class LeagueDuesPaymentUpdate(SQLModel):
    golfer_id: Optional[int] = None
    year: Optional[int] = None
    type: Optional[LeagueDuesType] = None
    amount_due: Optional[float] = None
    amount_paid: Optional[float] = None
    is_paid: Optional[bool] = None
    linked_payment_id: Optional[int] = None
    method: Optional[PaymentMethod] = None
    comment: Optional[str] = None


class LeagueDuesPaymentRead(LeagueDuesPaymentBase):
    id: int


class TournamentEntryFeePaymentBase(SQLModel):
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    year: int
    tournament_id: int = Field(default=None, foreign_key="tournament.id")
    type: TournamentEntryFeeType = Field(
        sa_column=Column(
            SAEnum(
                TournamentEntryFeeType,
                name="tournament_entry_fee_type_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=False,
        )
    )
    amount_due: float
    amount_paid: Optional[float] = 0
    is_paid: Optional[bool] = False
    linked_payment_id: Optional[int] = None
    method: Optional[PaymentMethod] = Field(
        sa_column=Column(
            SAEnum(
                PaymentMethod,
                name="payment_method_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=True,
        )
    )
    comment: Optional[str] = None


class TournamentEntryFeePayment(TournamentEntryFeePaymentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TournamentEntryFeePaymentCreate(TournamentEntryFeePaymentBase):
    pass


class TournamentEntryFeePaymentUpdate(TournamentEntryFeePaymentBase):
    golfer_id: Optional[int] = None
    year: Optional[int] = None
    tournament_id: Optional[int] = None
    type: Optional[TournamentEntryFeeType] = None
    amount_due: Optional[float] = None
    amount_paid: Optional[float] = None
    is_paid: Optional[bool] = None
    linked_payment_id: Optional[int] = None
    method: Optional[PaymentMethod] = None
    comment: Optional[str] = None


class TournamentEntryFeePaymentRead(TournamentEntryFeePaymentBase):
    id: int
