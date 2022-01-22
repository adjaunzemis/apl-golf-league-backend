from enum import Enum
from sqlmodel import SQLModel, Field

class TeamRole(str, Enum):
    CAPTAIN = "Captain"
    PLAYER = "Player"
    SUBSTITUTE = "Substitute"

class TeamGolferLink(SQLModel, table=True):
    team_id: int = Field(default=None, foreign_key="team.id", primary_key=True)
    golfer_id: int = Field(default=None, foreign_key="golfer.id", primary_key=True)
    division_id: int = Field(default=None, foreign_key="division.id", primary_key=True)
    role: TeamRole
