from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .golfer import Golfer
from .team_golfer_link import TeamGolferLink

class TeamBase(SQLModel):
    name: str
    flight_id: int = Field(default=None, foreign_key="flight.id")

class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight: Optional["Flight"] = Relationship(back_populates="teams")
    golfers: List[Golfer] = Relationship(link_model=TeamGolferLink)

class TeamCreate(TeamBase):
    pass

class TeamUpdate(SQLModel):
    name: Optional[str] = None
    flight_id: Optional[int] = None

class TeamRead(TeamBase):
    id: int

class TeamReadWithGolfers(TeamRead):
    golfers: List[Golfer]

class TeamData(SQLModel):
    team_id: int
    flight_id: int
    name: str
    golfers: List[Golfer] = []
