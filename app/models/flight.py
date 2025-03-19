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
    secretary: str
    secretary_email: str | None = None
    secretary_phone: str | None = None
    signup_start_date: datetime
    signup_stop_date: datetime
    start_date: datetime
    weeks: int
    tee_times: str | None = None
    locked: bool = False


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


class FlightInfo(SQLModel):
    id: int
    year: int
    name: str
    course: str | None = None
    address: str | None = None
    phone: str | None = None
    logo_url: str | None = None
    secretary: str
    secretary_email: str | None = None
    signup_start_date: str
    signup_stop_date: str
    start_date: str
    weeks: int
    tee_times: str | None = None
    num_teams: int


class FlightTeamGolfer(BaseModel):
    golfer_id: int
    name: str
    role: TeamRole
    division: str


class FlightTeam(BaseModel):
    flight_id: int
    team_id: int
    name: str
    golfers: list[FlightTeamGolfer] = Field(default_factory=list)


class FlightStandingsTeam(BaseModel):
    team_id: int
    team_name: str
    points_won: float = 0
    matches_played: int = 0
    avg_points: float = 0
    position: str = ""


class FlightStandings(BaseModel):
    flight_id: int
    teams: list[FlightStandingsTeam]


class FlightStatisticsGolfer(BaseModel):
    golfer_id: int
    golfer_name: str
    golfer_team_id: int
    golfer_team_role: TeamRole
    num_matches: int = 0
    num_rounds: int = 0
    points_won: float = 0
    avg_points_won: float = 0
    avg_gross: float = 0
    avg_gross_to_par: float = 0
    avg_net: float = 0
    avg_net_to_par: float = 0
    num_holes: int = 0
    num_par_3_holes: int = 0
    num_par_4_holes: int = 0
    num_par_5_holes: int = 0
    avg_par_3_gross: float = 0
    avg_par_3_net: float = 0
    avg_par_4_gross: float = 0
    avg_par_4_net: float = 0
    avg_par_5_gross: float = 0
    avg_par_5_net: float = 0
    num_aces: int = 0
    num_albatrosses: int = 0
    num_eagles: int = 0
    num_birdies: int = 0
    num_pars: int = 0
    num_bogeys: int = 0
    num_double_bogeys: int = 0
    num_others: int = 0


class FlightStatistics(BaseModel):
    flight_id: int
    golfers: list[FlightStatisticsGolfer] = Field(default_factory=list)
