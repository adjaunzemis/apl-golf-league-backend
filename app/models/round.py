from typing import List, Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, date


from .tee import Tee, TeeRead
from .golfer import Golfer, GolferRead
from .round_golfer_link import RoundGolferLink
from .hole_result import HoleResult, HoleResultReadWithHole, HoleResultData

class RoundType(str, Enum):
    QUALIFYING = "Qualifying"
    FLIGHT = "Flight"
    PLAYOFF = "Playoff"
    TOURNAMENT = "Tournament"

class RoundBase(SQLModel):
    tee_id: int = Field(foreign_key="tee.id")
    type: RoundType
    date_played: date
    date_updated: datetime

class Round(RoundBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tee: Tee = Relationship()
    golfers: List[Golfer] = Relationship(link_model=RoundGolferLink)
    hole_results: List[HoleResult] = Relationship(back_populates="round")

class RoundCreate(RoundBase):
    pass

class RoundUpdate(SQLModel):
    tee_id: Optional[int] = None
    type: Optional[RoundType] = None
    date_played: Optional[date] = None
    date_updated: Optional[datetime] = None

class RoundRead(RoundBase):
    id: int

class RoundReadWithData(RoundRead):
    tee: Optional[TeeRead] = None
    golfers: Optional[List[GolferRead]] = None
    hole_results: Optional[List[HoleResultReadWithHole]] = None

class RoundData(SQLModel):
    round_id: int
    match_id: Optional[int] = None
    team_id: Optional[int] = None
    round_type: RoundType
    date_played: date
    date_updated: datetime
    golfer_id: int
    golfer_name: str
    golfer_handicap_index: float
    golfer_playing_handicap: int
    team_name: Optional[str] = None
    course_name: str
    tee_name: str
    tee_gender: str
    tee_rating: float
    tee_slope: float
    tee_par: int = None
    tee_color: str
    gross_score: int = None
    adjusted_gross_score: int = None
    net_score: int = None
    score_differential: float = None
    holes: List[HoleResultData] = []

class RoundDataWithCount(SQLModel):
    num_rounds: int
    rounds: List[RoundData]
