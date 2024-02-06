from typing import List, Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

from app.models.hole import Hole, HoleRead


class TeeGender(str, Enum):
    MENS = "Men's"
    LADIES = "Ladies'"


class TeeBase(SQLModel):
    name: str
    gender: TeeGender
    rating: float
    slope: int
    color: Optional[str]
    track_id: Optional[int] = Field(default=None, foreign_key="track.id")


class Tee(TeeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    track: Optional["Track"] = Relationship(back_populates="tees")
    holes: List[Hole] = Relationship(back_populates="tee")

    @property
    def par(self) -> int:
        return sum(hole.par for hole in self.holes)


class TeeCreate(TeeBase):
    pass


class TeeUpdate(SQLModel):
    name: Optional[str] = None
    gender: Optional[TeeGender] = None
    rating: Optional[float] = None
    slope: Optional[int] = None
    color: Optional[str] = None
    track_id: Optional[int] = None


class TeeRead(TeeBase):
    id: int


class TeeReadWithHoles(TeeRead):
    holes: List[HoleRead] = None
