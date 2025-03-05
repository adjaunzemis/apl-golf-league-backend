from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.course import Course
from app.models.division import Division, DivisionCreate
from app.models.flight_division_link import FlightDivisionLink
from app.models.flight_team_link import FlightTeamLink
from app.models.team import Team


class FlightBase(SQLModel):
    name: str
    year: int
    course_id: int = Field(default=None, foreign_key="course.id")
    logo_url: str | None = None
    secretary: str | None = None
    secretary_email: str | None = None
    secretary_phone: str | None = None
    signup_start_date: datetime | None = None
    signup_stop_date: datetime | None = None
    start_date: datetime | None = None
    weeks: int | None = None
    tee_times: str | None = None
    locked: bool | None = False


class Flight(FlightBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    course: Course = Relationship()
    divisions: list[Division] | None = Relationship(link_model=FlightDivisionLink)
    teams: list[Team] | None = Relationship(link_model=FlightTeamLink)


class FlightCreate(FlightBase):
    id: int | None = None
    divisions: list[DivisionCreate] = None


class FlightUpdate(SQLModel):
    name: str | None = None
    year: int | None = None
    course_id: int | None = None
    logo_url: str | None = None
    secretary: str | None = None
    secretary_email: str | None = None
    secretary_phone: str | None = None
    signup_start_date: datetime | None = None
    signup_stop_date: datetime | None = None
    start_date: datetime | None = None
    weeks: int | None = None
    tee_times: str | None = None
    locked: bool | None = None


class FlightRead(FlightBase):
    id: int
