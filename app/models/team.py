from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .golfer import Golfer
from .round import Round
from .flight_team_link import FlightTeamLink
from .tournament_team_link import TournamentTeamLink
from .team_golfer_link import TeamGolferLink

class TeamBase(SQLModel):
    name: str

class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight: Optional["Flight"] = Relationship(link_model=FlightTeamLink, sa_relationship_kwargs={'viewonly': True})
    tournament: Optional["Tournament"] = Relationship(link_model=TournamentTeamLink, sa_relationship_kwargs={'viewonly': True})
    golfers: List[Golfer] = Relationship(link_model=TeamGolferLink)

class TeamCreate(TeamBase):
    pass

class TeamUpdate(SQLModel):
    name: Optional[str] = None

class TeamRead(TeamBase):
    id: int

class FlightTeamReadWithGolfers(TeamRead):
    flight_id: int
    golfers: List[Golfer]

class TournamentTeamData(TeamRead):
    tournament_id: int
    golfers: List[Golfer]
    rounds: Optional[List[Round]] = []
