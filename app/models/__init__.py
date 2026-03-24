# Monkeypatch
#
# Forces SQLModel to use AutoString for Enum fields
# Matches behavior prior to v0.0.9
#
# Ref: https://github.com/tiangolo/sqlmodel/discussions/717
#
# TODO: Remove this, migrate to new enums?

from sqlmodel import main as _sqlmodel_main

_sqlmodel_main.sa_Enum = lambda _: _sqlmodel_main.AutoString

from app.models.course import Course
from app.models.division import Division
from app.models.flight import Flight, FlightFreeAgent
from app.models.flight_division_link import FlightDivisionLink
from app.models.flight_team_link import FlightTeamLink
from app.models.golfer import Golfer
from app.models.handicap import HandicapIndex
from app.models.hole import Hole
from app.models.hole_result import HoleResult
from app.models.match import Match
from app.models.match_round_link import MatchRoundLink
from app.models.officer import Officer
from app.models.payment import LeagueDues, LeagueDuesPayment, TournamentEntryFeePayment
from app.models.qualifying_score import QualifyingScore
from app.models.round import Round
from app.models.round_golfer_link import RoundGolferLink
from app.models.season import Season
from app.models.substitute import Substitute
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink
from app.models.tee import Tee
from app.models.tournament import Tournament, TournamentFreeAgent
from app.models.tournament_division_link import TournamentDivisionLink
from app.models.tournament_round_link import TournamentRoundLink
from app.models.tournament_team_link import TournamentTeamLink
from app.models.track import Track
from app.models.user import User

__all__ = [
    "Course",
    "Division",
    "Flight",
    "FlightDivisionLink",
    "FlightFreeAgent",
    "FlightTeamLink",
    "Golfer",
    "HandicapIndex",
    "Hole",
    "HoleResult",
    "LeagueDues",
    "LeagueDuesPayment",
    "Match",
    "MatchRoundLink",
    "Officer",
    "QualifyingScore",
    "Round",
    "RoundGolferLink",
    "Season",
    "Substitute",
    "Team",
    "TeamGolferLink",
    "Tee",
    "Tournament",
    "TournamentDivisionLink",
    "TournamentEntryFeePayment",
    "TournamentFreeAgent",
    "TournamentRoundLink",
    "TournamentTeamLink",
    "Track",
    "User",
]
