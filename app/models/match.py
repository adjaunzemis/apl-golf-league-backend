from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .flight import Flight, FlightRead
from .team import Team, TeamRead

class MatchBase(SQLModel):
    flight_id: int = Field(default=None, foreign_key="flight.id")
    week: int
    home_team_id: int = Field(default=None, foreign_key="team.id")
    away_team_id: int = Field(default=None, foreign_key="team.id")
    home_score: Optional[float] = None
    away_score: Optional[float] = None

class Match(MatchBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight: Flight = Relationship()
    home_team: Team = Relationship(sa_relationship_kwargs={"foreign_keys": "[Match.home_team_id]"})
    away_team: Team = Relationship(sa_relationship_kwargs={"foreign_keys": "[Match.away_team_id]"})

class MatchCreate(MatchBase):
    pass

class MatchUpdate(SQLModel):
    flight_id: Optional[int] = None
    week: Optional[int] = None
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    home_score: Optional[float] = None
    away_score: Optional[float] = None

class MatchRead(MatchBase):
    id: int

class MatchReadWithTeams(MatchRead):
    flight: FlightRead = None
    home_team: TeamRead = None
    away_team: TeamRead = None
