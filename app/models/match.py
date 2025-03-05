from enum import StrEnum

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
    home_score: float | None = None
    away_score: float | None = None


class Match(MatchBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    flight: Flight = Relationship()
    home_team: Team = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.home_team_id]"}
    )
    away_team: Team = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Match.away_team_id]"}
    )
    rounds: list[Round] = Relationship(link_model=MatchRoundLink)


class MatchCreate(MatchBase):
    pass


class MatchUpdate(SQLModel):
    flight_id: int | None = None
    week: int | None = None
    home_team_id: int | None = None
    away_team_id: int | None = None
    home_score: float | None = None
    away_score: float | None = None


class MatchRead(MatchBase):
    id: int


class MatchReadWithData(MatchRead):
    flight: FlightRead = None
    home_team: TeamRead = None
    away_team: TeamRead = None
    rounds: list[RoundReadWithData] = Field(default_factory=list)


class MatchSummary(BaseModel):
    match_id: int
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    flight_name: str
    week: int
    home_score: float | None = None
    away_score: float | None = None


class MatchData(MatchSummary):
    rounds: list[RoundResults] | None = Field(default_factory=list)


class MatchDataWithCount(BaseModel):
    num_matches: int
    matches: list[MatchData]


class MatchHoleWinner(StrEnum):
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
    home_team_rounds: list[RoundValidationRequest]
    away_team_rounds: list[RoundValidationRequest]


class MatchValidationResponse(BaseModel):
    home_team_rounds: list[RoundValidationResponse]
    away_team_rounds: list[RoundValidationResponse]
    home_team_score: float = 0.0
    away_team_score: float = 0.0
    hole_results: list[MatchHoleResult] = Field(default_factory=list)
    is_valid: bool = False
