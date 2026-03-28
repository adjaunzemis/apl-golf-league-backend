from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field

from app.models.base import APLGLBase, DisplayEnum
from app.models.team_golfer_link import TeamRole


class GolferAffiliation(DisplayEnum):
    APL_EMPLOYEE = "APL_EMPLOYEE"
    APL_RETIREE = "APL_RETIREE"
    APL_FAMILY = "APL_FAMILY"
    NON_APL_EMPLOYEE = "NON_APL_EMPLOYEE"


class GolferBase(APLGLBase):
    name: str
    affiliation: GolferAffiliation | None = Field(
        sa_column=Column(
            SAEnum(
                GolferAffiliation,
                name="golfer_affiliation_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=True,
        )
    )
    email: str | None = None
    phone: str | None = None
    handicap_index: float | None = None
    handicap_index_updated: datetime | None = None


class Golfer(GolferBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class GolferCreate(GolferBase):
    pass


class GolferUpdate(APLGLBase):
    name: str | None = None
    affiliation: GolferAffiliation | None = None
    email: str | None = None
    phone: str | None = None
    handicap_index: float | None = None
    handicap_index_updated: datetime | None = None


class GolferRead(GolferBase):
    id: int


class GolferStatisticsOLD(APLGLBase):
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


class GolferStatisticsScoring(APLGLBase):
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


class GolferStatistics(APLGLBase):
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


class GolferTeamData(APLGLBase):
    golfer_id: int
    golfer_name: str
    golfer_role: TeamRole
    division_id: int
    division_name: str
