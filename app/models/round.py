from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import date


from .tee import Tee, TeeRead
from .golfer import Golfer, GolferRead
from .hole_result import HoleResult, HoleResultReadWithHole
from .track import Track
from .course import Course

class RoundBase(SQLModel):
    tee_id: int = Field(foreign_key="tee.id")
    golfer_id: int = Field(foreign_key="golfer.id")
    handicap_index: float
    playing_handicap: int
    date_played: date

class Round(RoundBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tee: Tee = Relationship()
    golfer: Golfer = Relationship()
    hole_results: List[HoleResult] = Relationship(back_populates="round")

class RoundCreate(RoundBase):
    pass

class RoundUpdate(SQLModel):
    tee_id: Optional[int] = None
    golfer_id: Optional[int] = None
    handicap_index: Optional[float] = None
    playing_handicap: Optional[int] = None
    date_played: Optional[date] = None

class RoundRead(RoundBase):
    id: int

class RoundReadWithData(RoundRead):
    tee: Optional[TeeRead] = None
    golfer: Optional[GolferRead] = None
    hole_results: Optional[List[HoleResultReadWithHole]] = None

class RoundSummary(SQLModel):
    round_id: int
    date_played: date
    golfer_name: str
    golfer_handicap_index: float = None
    course_name: str
    tee_name: str
    tee_rating: float
    tee_slope: float
