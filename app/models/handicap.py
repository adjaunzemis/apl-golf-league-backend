from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

from app.models.golfer import Golfer
from app.models.round import Round


class HandicapIndexBase(SQLModel):
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    round_id: int = Field(default=None, foreign_key="round.id")
    date_posted: datetime = Field(default=None)
    round_number: int = Field(default=None)
    handicap_index: float = Field(default=None)


class HandicapIndex(HandicapIndexBase, table=True):
    id: int = Field(default=None, primary_key=True)
    golfer: Golfer = Relationship()
    round: Round = Relationship()


class HandicapIndexCreate(HandicapIndexBase):
    pass


class HandicapIndexUpdate(SQLModel):
    golfer_id: int | None = None
    round_id: int | None = None
    date_posted: datetime | None = None
    round_number: int | None = None
    handicap_index: float | None = None


class HandicapIndexRead(HandicapIndexBase):
    id: int
