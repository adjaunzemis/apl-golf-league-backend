from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

from .hole import Hole, HoleRead


class HoleResultBase(SQLModel):
    round_id: int = Field(foreign_key="round.id")
    hole_id: int = Field(foreign_key="hole.id")
    handicap_strokes: int
    gross_score: int
    adjusted_gross_score: int
    net_score: int


class HoleResult(HoleResultBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    round: Optional["Round"] = Relationship(back_populates="hole_results")
    hole: Hole = Relationship()


class HoleResultCreate(HoleResultBase):
    pass


class HoleResultUpdate(SQLModel):
    round_id: Optional[int] = None
    hole_id: Optional[int] = None
    handicap_strokes: Optional[int] = None
    gross_score: Optional[int] = None
    adjusted_gross_score: Optional[int] = None
    net_score: Optional[int] = None


class HoleResultRead(HoleResultBase):
    id: int


class HoleResultReadWithHole(HoleResultRead):
    hole: Optional[HoleRead] = None


# TODO: Remove this custom data class, consolidate with HoleResultRead*
class HoleResultData(SQLModel):
    hole_result_id: int
    round_id: int
    hole_id: int
    number: int
    par: int
    yardage: int = None
    stroke_index: int = None
    handicap_strokes: int = None
    gross_score: int
    adjusted_gross_score: int = None
    net_score: int = None


class HoleResultValidationRequest(BaseModel):
    number: int
    par: int
    stroke_index: int
    gross_score: int


class HoleResultValidationResponse(HoleResultValidationRequest):
    handicap_strokes: int
    adjusted_gross_score: int
    net_score: int
    max_gross_score: int
    is_valid: bool = False
