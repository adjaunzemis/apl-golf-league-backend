from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .tee import Tee, TeeReadWithHoles


class TrackBase(SQLModel):
    name: str
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")


class Track(TrackBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course: Optional["Course"] = Relationship(back_populates="tracks")
    tees: List[Tee] = Relationship(back_populates="track")


class TrackCreate(TrackBase):
    pass


class TrackUpdate(SQLModel):
    name: Optional[str] = None
    course_id: Optional[int] = None


class TrackRead(TrackBase):
    id: int


class TrackReadWithTees(TrackRead):
    tees: List[TeeReadWithHoles] = None
