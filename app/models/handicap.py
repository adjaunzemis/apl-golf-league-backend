from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.golfer import Golfer
from app.models.round import Round, RoundType, ScoringType


class HandicapIndexBase(SQLModel):
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    round_id: int = Field(default=None, foreign_key="round.id")
    date_posted: datetime = Field(default=None)
    round_number: int = Field(default=1)
    handicap_index: float = Field(default=None)


class HandicapIndex(HandicapIndexBase, table=True):
    id: int = Field(default=None, primary_key=True)
    golfer: Golfer = Relationship()
    round: Round = Relationship()


class HandicapIndexCreate(HandicapIndexBase):
    pass


class HandicapIndexUpdate(SQLModel):
    golfer_id: Optional[int] = None
    round_id: Optional[int] = None
    date_posted: Optional[datetime] = None
    round_number: Optional[int] = None
    handicap_index: Optional[float] = None


class HandicapIndexRead(HandicapIndexBase):
    id: int


class ScoringRecordRound(SQLModel):
    golfer_id: int
    golfer_name: str
    round_id: int | None
    date_played: datetime
    round_type: RoundType
    scoring_type: ScoringType
    course_name: str | None
    track_name: str | None
    tee_name: str | None
    tee_par: int | None
    tee_rating: float | None
    tee_slope: int | None
    playing_handicap: int | None
    gross_score: int | None
    adjusted_gross_score: int | None
    net_score: int | None
    score_differential: float
    handicap_index: float | None
