from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .track import Track

class CourseBase(SQLModel):
    name: str
    location: Optional[str]
    phone: Optional[str]
    website: Optional[str]

class Course(CourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracks: List[Track] = Relationship(back_populates="course")

class CourseCreate(CourseBase):
    pass

class CourseUpdate(SQLModel):
    name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

class CourseRead(CourseBase):
    id: int

class CourseReadWithTracks(CourseRead):
    tracks: List[Track] = None
