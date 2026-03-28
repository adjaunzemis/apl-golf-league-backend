from typing import Optional

from sqlmodel import Field, Relationship

from app.models.base import APLGLBase


class HoleBase(APLGLBase):
    number: int
    par: int
    yardage: Optional[int] = None
    stroke_index: int
    tee_id: Optional[int] = Field(default=None, foreign_key="tee.id")


class Hole(HoleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tee: Optional["Tee"] = Relationship(back_populates="holes")


class HoleCreate(HoleBase):
    pass


class HoleUpdate(APLGLBase):
    number: Optional[int] = None
    par: Optional[int] = None
    yardage: Optional[int] = None
    stroke_index: Optional[int] = None
    tee_id: Optional[int] = None


class HoleRead(HoleBase):
    id: int
