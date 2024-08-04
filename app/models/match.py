from enum import Enum
from typing import List, Optional

from pydantic.v1 import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from app.models.flight import Flight, FlightRead
from app.models.match_round_link import MatchRoundLink
from app.models.round import (
    Round,
    RoundReadWithData,
    RoundResults,
    RoundValidationRequest,
    RoundValidationResponse,
)
from app.models.team import Team, TeamRead


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
    rounds: Optional[List[RoundResults]] = []


class MatchDataWithCount(SQLModel):
    num_matches: int
    matches: List[MatchData]


class MatchHoleWinner(str, Enum):
    """Indicates which team won the hole during the match."""

    HOME = "Home"
    AWAY = "Away"
    TIE = "Tie"


class MatchHoleResult(BaseModel):
    """Container for results from a hole in a match."""

    home_team_gross_score: int
    home_team_net_score: int
    home_team_handicap_strokes: int
    away_team_gross_score: int
    away_team_net_score: int
    away_team_handicap_strokes: int
    winner: MatchHoleWinner


class MatchValidationRequest(BaseModel):
    home_team_rounds: List[RoundValidationRequest]
    away_team_rounds: List[RoundValidationRequest]


class MatchValidationResponse(BaseModel):
    home_team_rounds: List[RoundValidationResponse]
    away_team_rounds: List[RoundValidationResponse]
    home_team_score: float = 0.0
    away_team_score: float = 0.0
    hole_results: List[MatchHoleResult] = []
    is_valid: bool = False
