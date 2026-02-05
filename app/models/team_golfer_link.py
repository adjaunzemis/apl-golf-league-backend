from enum import StrEnum

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel


class TeamRole(StrEnum):
    CAPTAIN = "Captain"
    PLAYER = "Player"
    SUBSTITUTE = "Substitute"


class TeamGolferLink(SQLModel, table=True):
    team_id: int = Field(default=None, foreign_key="team.id", primary_key=True)
    golfer_id: int = Field(default=None, foreign_key="golfer.id", primary_key=True)
    division_id: int = Field(default=None, foreign_key="division.id")
    role: TeamRole = Field(
        sa_column=Column(
            SAEnum(
                TeamRole,
                name="team_role_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=False,
        )
    )
