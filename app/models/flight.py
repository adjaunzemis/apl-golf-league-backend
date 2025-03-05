from datetime import datetime

from pydantic.v1 import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.course import Course
from app.models.division import Division, DivisionCreate
from app.models.flight_division_link import FlightDivisionLink
from app.models.flight_team_link import FlightTeamLink
from app.models.team import Team
from app.models.team_golfer_link import TeamRole


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


class FlightTeamGolfer(BaseModel):
    golfer_id: int
    name: str
    role: TeamRole


class FlightTeam(BaseModel):
    flight_id: int
    team_id: int
    name: str
    golfers: list[FlightTeamGolfer] = Field(default_factory=list)


class FlightStandingsTeam(BaseModel):
    team_id: int
    team_name: str
    points_won: float
    matches_played: int
    avg_points: float
    position: str


class FlightStandings(BaseModel):
    flight_id: int
    teams: list[FlightStandingsTeam]
