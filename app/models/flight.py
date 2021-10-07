from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from ..models.course import Course
from ..models.division import Division, DivisionRead

class FlightBase(SQLModel):
    name: str
    year: int
    home_course_id: int = Field(default=None, foreign_key="course.id")

class Flight(FlightBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    home_course: Course = Relationship()
    divisions: Optional[List[Division]] = Relationship(back_populates="flight")

class FlightCreate(FlightBase):
    pass

class FlightUpdate(SQLModel):
    name: Optional[str] = None
    year: Optional[int] = None
    home_course_id: Optional[int] = None

class FlightRead(FlightBase):
    id: int

class FlightReadWithDivisions(FlightRead):
    divisions: List[DivisionRead] = []
