from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .course import Course
from .division import Division, DivisionRead, DivisionData
from .team import Team, TeamRead

class FlightBase(SQLModel):
    name: str
    year: int
    home_course_id: int = Field(default=None, foreign_key="course.id")

class Flight(FlightBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    home_course: Course = Relationship()
    divisions: Optional[List[Division]] = Relationship(back_populates="flight")
    teams: Optional[List[Team]] = Relationship(back_populates="flight")

class FlightCreate(FlightBase):
    pass

class FlightUpdate(SQLModel):
    name: Optional[str] = None
    year: Optional[int] = None
    home_course_id: Optional[int] = None

class FlightRead(FlightBase):
    id: int

class FlightReadWithData(FlightRead):
    divisions: List[DivisionRead] = []
    teams: List[TeamRead] = []

class FlightData(SQLModel):
    flight_id: int
    year: int
    name: str
    home_course_name: str = None
    divisions: List[DivisionData] = []
    teams: List[TeamRead] = []

class FlightDataWithCount(SQLModel):
    num_flights: int
    flights: List[FlightData]
