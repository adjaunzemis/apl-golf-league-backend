from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

from .course import Course
from .division import Division
from .tournament_division_link import TournamentDivisionLink
from .team import Team
from .tournament_team_link import TournamentTeamLink

class TournamentBase(SQLModel):
    name: str
    year: int
    date: Optional[datetime] = None
    course_id: int = Field(default=None, foreign_key="course.id")
    logo_url: Optional[str] = None
    secretary: Optional[str] = None
    secretary_email: Optional[str] = None
    secretary_phone: Optional[str] = None
    signup_start_date: Optional[datetime] = None
    signup_stop_date: Optional[datetime] = None
    members_entry_fee: Optional[float] = None
    non_members_entry_fee: Optional[float] = None
    locked: Optional[bool] = False

class Tournament(TournamentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course: Course = Relationship()
    divisions: Optional[List[Division]] = Relationship(link_model=TournamentDivisionLink)
    teams: Optional[List[Team]] = Relationship(link_model=TournamentTeamLink)

class TournamentCreate(TournamentBase):
    pass

class TournamentUpdate(SQLModel):
    name: Optional[str] = None
    year: Optional[int] = None
    date: Optional[datetime] = None
    course_id: Optional[int] = None
    logo_url: Optional[str] = None
    secretary: Optional[str] = None
    secretary_email: Optional[str] = None
    secretary_phone: Optional[str] = None
    signup_start_date: Optional[datetime] = None
    signup_stop_date: Optional[datetime] = None
    members_entry_fee: Optional[float] = None
    non_members_entry_fee: Optional[float] = None
    locked: Optional[bool] = None

class TournamentRead(TournamentBase):
    id: int
    # course: Optional[Course] = None # TODO: try using this instead of joins in query?
