from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.course import Course
from app.models.division import Division, DivisionCreate
from app.models.team import Team
from app.models.tournament_division_link import TournamentDivisionLink
from app.models.tournament_team_link import TournamentTeamLink


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
    shotgun: Optional[bool] = False
    strokeplay: Optional[bool] = False
    bestball: Optional[int] = 0
    scramble: Optional[bool] = False
    ryder_cup: Optional[bool] = False
    individual: Optional[bool] = False
    chachacha: Optional[bool] = False
    locked: Optional[bool] = False


class Tournament(TournamentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course: Course = Relationship()
    divisions: Optional[List[Division]] = Relationship(
        link_model=TournamentDivisionLink
    )
    teams: Optional[List[Team]] = Relationship(link_model=TournamentTeamLink)


class TournamentCreate(TournamentBase):
    id: Optional[int] = None
    divisions: Optional[List[DivisionCreate]] = None


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
    shotgun: Optional[bool] = None
    strokeplay: Optional[bool] = None
    bestball: Optional[int] = None
    scramble: Optional[bool] = None
    ryder_cup: Optional[bool] = None
    individual: Optional[bool] = None
    chachacha: Optional[bool] = None
    locked: Optional[bool] = None


class TournamentRead(TournamentBase):
    id: int
    # course: Optional[Course] = None # TODO: try using this instead of joins in query?
