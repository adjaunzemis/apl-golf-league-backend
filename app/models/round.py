from datetime import date, datetime
from typing import Union

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship

from app.models.base import APLGLBaseModel, DisplayEnum
from app.models.golfer import Golfer, GolferRead
from app.models.hole_result import (
    HoleResult,
    HoleResultData,
    HoleResultReadWithHole,
    HoleResultSubmissionResponse,
    HoleResultValidationRequest,
    HoleResultValidationResponse,
)
from app.models.round_golfer_link import RoundGolferLink
from app.models.tee import Tee, TeeGender, TeeRead


class RoundType(DisplayEnum):
    QUALIFYING = "QUALIFYING"
    FLIGHT = "FLIGHT"
    PLAYOFF = "PLAYOFF"
    TOURNAMENT = "TOURNAMENT"


class ScoringType(DisplayEnum):
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"


class RoundBase(APLGLBaseModel):
    tee_id: int = Field(foreign_key="tee.id")
    type: RoundType = Field(
        sa_column=Column(
            SAEnum(
                RoundType,
                name="round_type_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=False,
        )
    )
    scoring_type: ScoringType | None = Field(
        sa_column=Column(
            SAEnum(
                ScoringType,
                name="scoring_type_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=True,
        )
    )
    date_played: datetime
    date_updated: datetime


class Round(RoundBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tee: Tee = Relationship()
    golfers: list[Golfer] = Relationship(link_model=RoundGolferLink)
    hole_results: list[HoleResult] = Relationship(back_populates="round")


class RoundCreate(RoundBase):
    pass


class RoundUpdate(APLGLBaseModel):
    tee_id: int | None = None
    type: RoundType | None = None
    scoring_type: ScoringType | None = None
    date_played: datetime | None = None
    date_updated: datetime | None = None


class RoundRead(RoundBase):
    id: int


class RoundReadWithData(RoundRead):
    tee: TeeRead | None = None
    golfers: list[GolferRead] | None = None
    hole_results: list[HoleResultReadWithHole] | None = None


class RoundSummary(APLGLBaseModel):
    round_id: int | None = None
    date_played: datetime | None = None
    round_type: RoundType | None = None
    golfer_name: str | None = None
    golfer_playing_handicap: int | None = None
    course_name: str | None = None
    track_name: str | None = None
    tee_name: str | None = None
    tee_gender: TeeGender | None = None
    tee_par: int | None = None
    tee_rating: float | None = None
    tee_slope: float | None = None
    gross_score: int | None = None
    adjusted_gross_score: int | None = None
    net_score: int | None = None
    score_differential: float | None = None


class RoundSummaryHandicap(RoundSummary):
    is_counting: bool


class RoundResults(APLGLBaseModel):
    round_id: int
    match_id: int | None = None
    team_id: int | None = None
    round_type: RoundType
    date_played: datetime
    date_updated: datetime
    golfer_id: int
    golfer_name: str
    golfer_playing_handicap: int | None = None
    role: str | None = None
    team_name: str | None = None
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
    holes: list[HoleResultData] = Field(default_factory=list)


class RoundResultsWithCount(APLGLBaseModel):
    num_rounds: int
    rounds: list[RoundResults]


class RoundValidationRequest(APLGLBaseModel):
    date_played: Union[datetime, date]
    course_handicap: int
    holes: list[HoleResultValidationRequest] = Field(default_factory=list)


class RoundValidationResponse(APLGLBaseModel):
    date_played: Union[datetime, date]
    course_handicap: int
    holes: list[HoleResultValidationResponse] = Field(default_factory=list)
    is_valid: bool = False


class RoundSubmissionRequest(RoundValidationRequest):
    golfer_id: int
    tee_id: int
    round_type: RoundType
    scoring_type: ScoringType


class RoundSubmissionResponse(APLGLBaseModel):
    round_id: int
    golfer_id: int
    tee_id: int
    round_type: RoundType
    scoring_type: ScoringType
    date_played: Union[datetime, date]
    course_handicap: int
    holes: list[HoleResultSubmissionResponse] = Field(default_factory=list)
    is_valid: bool = False
