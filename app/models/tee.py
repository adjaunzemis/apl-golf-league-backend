from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship

from app.models.base import APLGLBaseModel, DisplayEnum
from app.models.hole import Hole, HoleRead


class TeeGender(DisplayEnum):
    MENS = "MENS"
    LADIES = "LADIES"


TeeGender._custom_labels = {  # initialize custom labels
    TeeGender.MENS: "Men's",
    TeeGender.LADIES: "Ladies'",
}


class TeeBase(APLGLBaseModel):
    name: str
    gender: TeeGender = Field(
        sa_column=Column(
            SAEnum(
                TeeGender,
                name="tee_gender_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=False,
        )
    )
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


class TeeUpdate(APLGLBaseModel):
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
