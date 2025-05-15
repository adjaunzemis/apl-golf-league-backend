from datetime import datetime
from enum import Enum

from pydantic.v1 import BaseModel
from sqlmodel import Field, SQLModel

from app.models.team_golfer_link import TeamRole


class GolferAffiliation(str, Enum):
    APL_EMPLOYEE = "APL Employee"
    APL_RETIREE = "APL Retiree"
    APL_FAMILY = "APL Family"
    NON_APL_EMPLOYEE = "Non-APL Employee"


class GolferBase(SQLModel):
    name: str
    affiliation: GolferAffiliation | None = None
    email: str | None = None
    phone: str | None = None
    handicap_index: float | None = None
    handicap_index_updated: datetime | None = None


class Golfer(GolferBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class GolferCreate(GolferBase):
    pass


class GolferUpdate(SQLModel):
    name: str | None = None
    affiliation: GolferAffiliation | None = None
    email: str | None = None
    phone: str | None = None
    handicap_index: float | None = None
    handicap_index_updated: datetime | None = None


class GolferRead(GolferBase):
    id: int


class GolferStatisticsOLD(SQLModel):
    num_rounds: int = 0
    num_holes: int = 0
    avg_gross_score: float = 0
    avg_net_score: float = 0
    num_aces: int = 0
    num_albatrosses: int = 0
    num_eagles: int = 0
    num_birdies: int = 0
    num_pars: int = 0
    num_bogeys: int = 0
    num_double_bogeys: int = 0
    num_others: int = 0


class GolferStatisticsScoring(BaseModel):
    avg_score: float = 0
    avg_score_to_par: float = 0
    avg_par_3_score: float = 0
    avg_par_4_score: float = 0
    avg_par_5_score: float = 0
    num_aces: int = 0
    num_albatrosses: int = 0
    num_eagles: int = 0
    num_birdies: int = 0
    num_pars: int = 0
    num_bogeys: int = 0
    num_double_bogeys: int = 0
    num_others: int = 0


class GolferStatistics(BaseModel):
    golfer_id: int
    golfer_name: str
    num_rounds: int = 0
    num_holes: int = 0
    num_par_3_holes: int = 0
    num_par_4_holes: int = 0
    num_par_5_holes: int = 0
    gross_scoring: GolferStatisticsScoring = GolferStatisticsScoring()
    net_scoring: GolferStatisticsScoring = GolferStatisticsScoring()


class TeamGolferStatistics(GolferStatistics):
    golfer_team_id: int
    golfer_team_role: TeamRole


class GolferTeamData(BaseModel):
    golfer_id: int
    golfer_name: str
    golfer_role: TeamRole
    division_id: int
    division_name: str
