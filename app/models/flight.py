from typing import List, Optional
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

from .course import Course
from .division import Division
from .team import Team
from .flight_team_link import FlightTeamLink
from .flight_division_link import FlightDivisionLink

class FlightBase(SQLModel):
    name: str
    year: int
    course_id: int = Field(default=None, foreign_key="course.id")
    logo_url: Optional[str] = None
    secretary: Optional[str] = None
    secretary_email: Optional[str] = None
    secretary_phone: Optional[str] = None
    signup_begin: Optional[date] = None
    signup_end: Optional[date] = None
    start_date: Optional[date] = None
    weeks: Optional[int] = None
    locked: Optional[bool] = False

class Flight(FlightBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course: Course = Relationship()
    divisions: Optional[List[Division]] = Relationship(link_model=FlightDivisionLink)
    teams: Optional[List[Team]] = Relationship(link_model=FlightTeamLink)

class FlightCreate(FlightBase):
    pass

class FlightUpdate(SQLModel):
    name: Optional[str] = None
    year: Optional[int] = None
    course_id: Optional[int] = None
    logo_url: Optional[str] = None
    secretary: Optional[str] = None
    secretary_email: Optional[str] = None
    secretary_phone: Optional[str] = None
    signup_begin: Optional[date] = None
    signup_end: Optional[date] = None
    start_date: Optional[date] = None
    weeks: Optional[int] = None
    locked: Optional[bool] = None

class FlightRead(FlightBase):
    id: int
