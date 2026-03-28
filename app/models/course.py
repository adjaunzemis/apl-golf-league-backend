from typing import List, Optional

from sqlmodel import Field, Relationship

from app.models.base import APLGLBase
from app.models.track import Track, TrackReadWithTees


class CourseBase(APLGLBase):
    name: str
    year: int
    address: Optional[str]
    phone: Optional[str]
    website: Optional[str]


class Course(CourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tracks: List[Track] = Relationship(back_populates="course")


class CourseCreate(CourseBase):
    pass


class CourseUpdate(APLGLBase):
    name: Optional[str] = None
    year: Optional[int] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


class CourseRead(CourseBase):
    id: int


class CourseReadWithTracks(CourseRead):
    tracks: List[TrackReadWithTees] = None
