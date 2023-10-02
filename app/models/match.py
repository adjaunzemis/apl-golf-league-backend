from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from enum import Enum

from .flight import Flight, FlightRead
from .team import Team, TeamRead
from .round import (
    Round,
    RoundReadWithData,
    RoundData,
    RoundValidationRequest,
    RoundValidationResponse,
)
from .match_round_link import MatchRoundLink


class MatchHoleResult(str, Enum):
    """Indicates which team won the hole during the match."""

    HOME = "Home"
    AWAY = "Away"
    TIE = "Tie"


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
    home_team: Team = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.home_team_id]"}
    )
    away_team: Team = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.away_team_id]"}
    )
    rounds: List[Round] = Relationship(link_model=MatchRoundLink)


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


class MatchReadWithData(MatchRead):
    flight: FlightRead = None
    home_team: TeamRead = None
    away_team: TeamRead = None
    rounds: List[RoundReadWithData] = []


class MatchSummary(SQLModel):
    match_id: int
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    flight_name: str
    week: int
    home_score: Optional[float] = None
    away_score: Optional[float] = None


class MatchData(MatchSummary):
    rounds: Optional[List[RoundData]] = []


class MatchDataWithCount(SQLModel):
    num_matches: int
    matches: List[MatchData]


class MatchValidationRequest(BaseModel):
    home_team_rounds: List[RoundValidationRequest]
    away_team_rounds: List[RoundValidationRequest]


class MatchValidationResponse(BaseModel):
    home_team_rounds: List[RoundValidationResponse]
    away_team_rounds: List[RoundValidationResponse]
    home_team_score: float = 0.0
    away_team_score: float = 0.0
    hole_results: List[MatchHoleResult] = []  # TODO: Expand with handicap strokes?
    is_valid: bool = False
