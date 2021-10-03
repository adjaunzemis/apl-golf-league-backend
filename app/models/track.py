from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class TrackBase(SQLModel):
    name: str
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")

class Track(TrackBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course: Optional["Course"] = Relationship(back_populates="tracks")

class TrackCreate(TrackBase):
    pass

class TrackUpdate(SQLModel):
    name: Optional[str] = None
    id: Optional[str] = None
    course_id: Optional[int] = None

class TrackRead(TrackBase):
    id: int

class TrackReadwithCourse(TrackRead):
    course: Optional["Course"] = None

# TODO: TrackReadWithTees
