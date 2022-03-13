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

class LeagueDuesBase(SQLModel):
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    year: int
    type: LeagueDuesType
    amount: float
    paid: Optional[bool] = False
    method: Optional[PaymentMethod] = None
    confirmation: Optional[str] = None

class LeagueDues(LeagueDuesBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class LeagueDuesCreate(LeagueDuesBase):
    pass

class LeagueDuesUpdate(SQLModel):
    golfer_id: Optional[int] = None
    year: Optional[int] = None
    type: Optional[LeagueDuesType] = None
    amount: Optional[float] = None
    paid: Optional[bool] = None
    method: Optional[PaymentMethod] = None
    confirmation: Optional[str] = None

class LeagueDuesRead(LeagueDuesBase):
    id: int

class TournamentEntryFeeBase(SQLModel):
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    year: int
    tournament_id: int = Field(default=None, foreign_key="tournament.id")
    type: TournamentEntryFeeType
    amount: float
    paid: Optional[bool] = False
    method: Optional[PaymentMethod] = None
    confirmation: Optional[str] = None

class TournamentEntryFee(TournamentEntryFeeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class TournamentEntryFeeCreate(TournamentEntryFeeBase):
    pass

class TournamentEntryFeeUpdate(TournamentEntryFeeBase):
    golfer_id: Optional[int] = None
    year: Optional[int] = None
    tournament_id: Optional[int] = None
    type: Optional[TournamentEntryFeeType] = None
    amount: Optional[float] = None
    paid: Optional[bool] = None
    method: Optional[PaymentMethod] = None
    confirmation: Optional[str] = None

class TournamentEntryFeeRead(TournamentEntryFeeBase):
    id: int
