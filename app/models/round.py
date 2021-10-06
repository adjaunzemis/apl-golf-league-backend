from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import date

from ..models.tee import Tee, TeeRead
from ..models.golfer import Golfer, GolferRead

class RoundBase(SQLModel):
    tee_id: Optional[int] = Field(default=None, foreign_key="tee.id")
    golfer_id: Optional[int] = Field(default=None, foreign_key="golfer.id")
    handicap_index: Optional[float] = None
    playing_handicap: Optional[float] = None
    date_played: Optional[date] = None

class Round(RoundBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tee: Optional[Tee] = Relationship()
    golfer: Optional[Golfer] = Relationship()

class RoundCreate(RoundBase):
    pass

class RoundUpdate(SQLModel):
    tee_id: Optional[int] = None
    golfer_id: Optional[int] = None
    handicap_index: Optional[float] = None
    playing_handicap: Optional[float] = None
    date_played: Optional[date] = None

class RoundRead(RoundBase):
    id: int

class RoundReadWithTeeAndGolfer(RoundRead):
    tee: Optional[TeeRead] = None
    golfer: Optional[GolferRead] = None
