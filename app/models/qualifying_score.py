from datetime import datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel

from app.models.golfer import Golfer
from app.models.tee import TeeGender


class QualifyingScoreType(StrEnum):
    QUALIFYING_ROUND = "Qualifying Round"
    OFFICIAL_HANDICAP_INDEX = "Official Handicap Index"


class QualifyingScoreBase(SQLModel):
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    year: int
    type: QualifyingScoreType = Field(
        sa_column=Column(
            SAEnum(
                QualifyingScoreType,
                name="qualifying_score_type_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=False,
        )
    )
    score_differential: float
    date_updated: datetime
    date_played: Optional[datetime] = None
    course_name: Optional[str] = None
    track_name: Optional[str] = None
    tee_name: Optional[str] = None
    tee_gender: Optional[TeeGender] = None
    tee_par: Optional[int] = None
    tee_rating: Optional[float] = None
    tee_slope: Optional[float] = None
    gross_score: Optional[int] = None
    adjusted_gross_score: Optional[int] = None
    comment: Optional[str] = None


class QualifyingScore(QualifyingScoreBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    golfer: Golfer = Relationship()


class QualifyingScoreCreate(QualifyingScoreBase):
    pass


class QualifyingScoreUpdate(SQLModel):
    golfer_id: Optional[int] = None
    year: Optional[int] = None
    type: Optional[QualifyingScoreType] = None
    score_differential: Optional[float] = None
    date_updated: Optional[datetime] = None
    date_played: Optional[datetime] = None
    course_name: Optional[str] = None
    track_name: Optional[str] = None
    tee_name: Optional[str] = None
    tee_gender: Optional[TeeGender] = None
    tee_par: Optional[int] = None
    tee_rating: Optional[float] = None
    tee_slope: Optional[float] = None
    gross_score: Optional[int] = None
    adjusted_gross_score: Optional[int] = None
    comment: Optional[str] = None


class QualifyingScoreRead(QualifyingScoreBase):
    id: int
