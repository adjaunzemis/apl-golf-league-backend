from typing import List, Optional
from sqlmodel import SQLModel, Field

class CourseBase(SQLModel):
    name: str
    location: Optional[str]
    phone: Optional[str]
    website: Optional[str]

class Course(CourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class CourseCreate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int

class CourseUpdate(SQLModel):
    name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

# TODO: CourseReadWithTracks
