from typing import Optional
from enum import Enum
from sqlmodel import Field, SQLModel

class LeagueDuesType(str, Enum):
    FLIGHT_DUES = "Flight Dues"
    TOURNAMENT_ONLY_DUES = "Tournament-Only Dues"

class TournamentEntryFeeType(str, Enum):
    MEMBER_FEE = "Member Fee"
    NON_MEMBER_FEE = "Non-Member Fee"

class PaymentMethod(str, Enum):
    CASH_OR_CHECK = "Cash or Check"
    PAYPAL = "PayPal"
    EXEMPT = "Exempt"
    LINKED = "Linked"

class LeagueDuesBase(SQLModel):
    year: int
    type: LeagueDuesType
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
    method: Optional[PaymentMethod] = None
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
    type: TournamentEntryFeeType
    amount_due: float
    amount_paid: Optional[float] = 0
    is_paid: Optional[bool] = False
    linked_payment_id: Optional[int] = None
    method: Optional[PaymentMethod] = None
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
