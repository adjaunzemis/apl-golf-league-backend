from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field

from app.models.base import APLGLBase, DisplayEnum


class LeagueDuesType(DisplayEnum):
    FLIGHT_DUES = "FLIGHT_DUES"
    TOURNAMENT_ONLY_DUES = "TOURNAMENT_ONLY_DUES"


class TournamentEntryFeeType(DisplayEnum):
    MEMBER_FEE = "MEMBER_FEE"
    NON_MEMBER_FEE = "NON_MEMBER_FEE"


class PaymentMethod(DisplayEnum):
    CASH_OR_CHECK = "CASH_OR_CHECK"
    PAYPAL = "PAYPAL"
    EXEMPT = "EXEMPT"
    LINKED = "LINKED"


class LeagueDuesBase(APLGLBase):
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


class LeagueDuesUpdate(APLGLBase):
    year: Optional[int] = None
    type: Optional[LeagueDuesType] = None
    amount: Optional[float] = None


class LeagueDuesRead(LeagueDuesBase):
    id: int


class LeagueDuesPaymentBase(APLGLBase):
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


class LeagueDuesPaymentUpdate(APLGLBase):
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


class TournamentEntryFeePaymentBase(APLGLBase):
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
