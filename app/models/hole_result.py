from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .hole import Hole, HoleRead

class HoleResultBase(SQLModel):
    round_id: int = Field(foreign_key="round.id")
    hole_id: int = Field(foreign_key="hole.id")
    strokes: int

class HoleResult(HoleResultBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    round: Optional["Round"] = Relationship(back_populates="hole_results")
    hole: Hole = Relationship()

class HoleResultCreate(HoleResultBase):
    pass

class HoleResultUpdate(SQLModel):
    round_id: Optional[int] = None
    hole_id: Optional[int] = None
    strokes: Optional[int] = None
    
class HoleResultRead(HoleResultBase):
    id: int

class HoleResultReadWithHole(HoleResultRead):
    hole: Optional[HoleRead] = None

class HoleResultData(SQLModel):
    hole_result_id: int
    round_id: int
    number: int
    par: int
    yardage: int = None
    stroke_index: int = None
    handicap_strokes: int = None
    gross_score: int
    adjusted_gross_score: int = None
    net_score: int = None
