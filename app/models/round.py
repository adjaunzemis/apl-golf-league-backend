from typing import List, Optional, Union
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from datetime import datetime, date

from .tee import Tee, TeeGender, TeeRead
from .golfer import Golfer, GolferRead
from .round_golfer_link import RoundGolferLink
from .hole_result import (
    HoleResult,
    HoleResultReadWithHole,
    HoleResultData,
    HoleResultValidationRequest,
    HoleResultValidationResponse,
)


class RoundType(str, Enum):
    QUALIFYING = "Qualifying"
    FLIGHT = "Flight"
    PLAYOFF = "Playoff"
    TOURNAMENT = "Tournament"


class ScoringType(str, Enum):
    INDIVIDUAL = "Individual"
    GROUP = "Group"


class RoundBase(SQLModel):
    tee_id: int = Field(foreign_key="tee.id")
    type: RoundType
    scoring_type: Optional[ScoringType] = None
    date_played: datetime
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
    scoring_type: Optional[ScoringType] = None
    date_played: Optional[datetime] = None
    date_updated: Optional[datetime] = None


class RoundRead(RoundBase):
    id: int


class RoundReadWithData(RoundRead):
    tee: Optional[TeeRead] = None
    golfers: Optional[List[GolferRead]] = None
    hole_results: Optional[List[HoleResultReadWithHole]] = None


class RoundSummary(SQLModel):
    round_id: Optional[int] = None
    date_played: Optional[datetime] = None
    round_type: Optional[RoundType] = None
    golfer_name: Optional[str] = None
    golfer_playing_handicap: Optional[int] = None
    course_name: Optional[str] = None
    track_name: Optional[str] = None
    tee_name: Optional[str] = None
    tee_gender: Optional[TeeGender] = None
    tee_par: Optional[int] = None
    tee_rating: Optional[float] = None
    tee_slope: Optional[float] = None
    gross_score: Optional[int] = None
    adjusted_gross_score: Optional[int] = None
    net_score: Optional[int] = None
    score_differential: Optional[float] = None


class RoundData(SQLModel):
    round_id: int
    match_id: Optional[int] = None
    team_id: Optional[int] = None
    round_type: RoundType
    date_played: datetime
    date_updated: datetime
    golfer_id: int
    golfer_name: str
    golfer_playing_handicap: Optional[int] = None
    team_name: Optional[str] = None
    course_id: int
    course_name: str
    track_id: int
    track_name: str
    tee_id: int
    tee_name: str
    tee_gender: str
    tee_par: int
    tee_rating: float
    tee_slope: float
    tee_color: str
    gross_score: int = None
    adjusted_gross_score: int = None
    net_score: int = None
    score_differential: float = None
    holes: List[HoleResultData] = []


class RoundDataWithCount(SQLModel):
    num_rounds: int
    rounds: List[RoundData]


class RoundValidationRequest(BaseModel):
    date_played: Union[datetime, date]
    course_handicap: int
    holes: List[HoleResultValidationRequest] = []


class RoundValidationResponse(BaseModel):
    date_played: Union[datetime, date]
    course_handicap: int
    holes: List[HoleResultValidationResponse] = []
    is_valid: bool = False
