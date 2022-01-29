from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .course import Course
from .division import Division, DivisionRead
from .team import Team, TeamRead
from .flight_team_link import FlightTeamLink

class FlightBase(SQLModel):
    name: str
    year: int
    home_course_id: int = Field(default=None, foreign_key="course.id")
    logo_url: Optional[str] = None
    secretary: Optional[str] = None
    secretary_contact: Optional[str] = None

class Flight(FlightBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    home_course: Course = Relationship()
    divisions: Optional[List[Division]] = Relationship(back_populates="flight")
    teams: Optional[List[Team]] = Relationship(link_model=FlightTeamLink)

class FlightCreate(FlightBase):
    pass

class FlightUpdate(SQLModel):
    name: Optional[str] = None
    year: Optional[int] = None
    home_course_id: Optional[int] = None
    logo_url: Optional[str] = None
    secretary: Optional[str] = None
    secretary_contact: Optional[str] = None

class FlightRead(FlightBase):
    id: int

class FlightReadWithData(FlightRead):
    divisions: List[DivisionRead] = []
    teams: List[TeamRead] = []
