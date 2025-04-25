from datetime import datetime

from pydantic.v1 import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.course import Course
from app.models.division import Division, DivisionCreate
from app.models.golfer import Golfer, GolferStatistics
from app.models.team import Team
from app.models.team_golfer_link import TeamRole
from app.models.tournament_division_link import TournamentDivisionLink
from app.models.tournament_team_link import TournamentTeamLink


class TournamentBase(SQLModel):
    name: str
    year: int
    date: datetime | None = None
    course_id: int = Field(default=None, foreign_key="course.id")
    logo_url: str | None = None
    secretary: str | None = None
    secretary_email: str | None = None
    secretary_phone: str | None = None
    signup_start_date: datetime | None = None
    signup_stop_date: datetime | None = None
    members_entry_fee: float | None = None
    non_members_entry_fee: float | None = None
    shotgun: bool | None = False
    strokeplay: bool | None = False
    bestball: int | None = 0
    scramble: bool | None = False
    ryder_cup: bool | None = False
    individual: bool | None = False
    chachacha: bool | None = False
    locked: bool | None = False


class Tournament(TournamentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    course: Course = Relationship()
    divisions: list[Division] | None = Relationship(link_model=TournamentDivisionLink)
    teams: list[Team] | None = Relationship(link_model=TournamentTeamLink)


class TournamentCreate(TournamentBase):
    id: int | None = None
    divisions: list[DivisionCreate] | None = None


class TournamentUpdate(SQLModel):
    name: str | None = None
    year: int | None = None
    date: datetime | None = None
    course_id: int | None = None
    logo_url: str | None = None
    secretary: str | None = None
    secretary_email: str | None = None
    secretary_phone: str | None = None
    signup_start_date: datetime | None = None
    signup_stop_date: datetime | None = None
    members_entry_fee: float | None = None
    non_members_entry_fee: float | None = None
    shotgun: bool | None = None
    strokeplay: bool | None = None
    bestball: int | None = None
    scramble: bool | None = None
    ryder_cup: bool | None = None
    individual: bool | None = None
    chachacha: bool | None = None
    locked: bool | None = None


class TournamentRead(TournamentBase):
    id: int
    # course: Optional[Course] = None # TODO: try using this instead of joins in query?


class TournamentInfo(SQLModel):
    id: int
    year: int
    name: str
    date: str = None
    course: str = None
    address: str = None
    phone: str = None
    logo_url: str = None
    secretary: str
    secretary_email: str = None
    signup_start_date: str = None
    signup_stop_date: str = None
    members_entry_fee: float = None
    non_members_entry_fee: float = None
    shotgun: bool = False
    strokeplay: bool = False
    bestball: int = 0
    scramble: bool = False
    ryder_cup: bool = False
    individual: bool = False
    chachacha: bool = False
    num_teams: int


class TournamentTeamGolfer(BaseModel):
    golfer_id: int
    name: str
    role: TeamRole
    division: str
    handicap_index: float | None
    email: str | None


class TournamentTeam(BaseModel):
    tournament_id: int
    team_id: int
    name: str
    golfers: list[TournamentTeamGolfer] = Field(default_factory=list)


class TournamentStandingsTeam(BaseModel):
    team_id: int
    team_name: str
    gross_score: int
    net_score: int
    position: str = ""


class TournamentStandingsGolfer(BaseModel):
    golfer_id: int
    golfer_name: str
    # division_name: str # TODO: pass this through tournament round data
    golfer_playing_handicap: int
    gross_score: int
    net_score: int
    position: str = ""


class TournamentStandings(BaseModel):
    tournament_id: int
    teams: list[TournamentStandingsTeam] = Field(default_factory=list)
    golfers: list[TournamentStandingsGolfer] = Field(default_factory=list)


class TournamentStatistics(BaseModel):
    tournament_id: int
    golfers: list[GolferStatistics] = Field(default_factory=list)


class TournamentFreeAgentBase(SQLModel):
    golfer_id: int = Field(foreign_key="golfer.id", primary_key=True)
    tournament_id: int = Field(foreign_key="tournament.id", primary_key=True)
    division_id: int = Field(foreign_key="division.id")


class TournamentFreeAgent(TournamentFreeAgentBase, table=True):
    golfer: Golfer = Relationship()
    tournament: Tournament = Relationship()
    division: Division = Relationship()


class TournamentFreeAgentCreate(TournamentFreeAgentBase):
    pass


class TournamentFreeAgentGolfer(TournamentTeamGolfer):
    pass
