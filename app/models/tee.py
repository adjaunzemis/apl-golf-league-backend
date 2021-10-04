from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .hole import Hole, HoleRead

class TeeBase(SQLModel):
    name: str
    gender: str
    rating: float
    slope: float
    color: Optional[str]
    track_id: Optional[int] = Field(default=None, foreign_key="track.id")

class Tee(TeeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    track: Optional["Track"] = Relationship(back_populates="tees")
    holes: List[Hole] = Relationship(back_populates="tee")

class TeeCreate(TeeBase):
    pass

class TeeUpdate(SQLModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    rating: Optional[float] = None
    slope: Optional[float] = None
    color: Optional[str] = None
    track_id: Optional[int] = None

class TeeRead(TeeBase):
    id: int

class TeeReadWithHoles(TeeRead):
    holes: List[HoleRead] = None
