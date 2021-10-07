from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .player import Player, PlayerRead

class TeamBase(SQLModel):
    name: Optional[str] = None
    flight_id: int = Field(default=None, foreign_key="flight.id")

class Team(TeamBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight: Optional["Flight"] = Relationship(back_populates="teams")
    players: Optional[List[Player]] = Relationship(back_populates="team")

class TeamCreate(TeamBase):
    pass

class TeamUpdate(SQLModel):
    name: Optional[str] = None
    flight_id: Optional[int] = None

class TeamRead(TeamBase):
    id: int

class TeamReadWithPlayers(TeamRead):
    players: List[PlayerRead] = []
