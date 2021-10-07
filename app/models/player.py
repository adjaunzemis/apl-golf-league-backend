from typing import List, Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

from ..models.golfer import Golfer, GolferRead

class PlayerRole(str, Enum):
    CAPTAIN = "CAPTAIN"
    PLAYER = "PLAYER"
    SUBSTITUTE = "SUBSTITUTE"

class PlayerBase(SQLModel):
    team_id: int = Field(default=None, foreign_key="team.id")
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    role: Optional[PlayerRole] = None

class Player(PlayerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    golfer: Golfer = Relationship()
    team: Optional["Team"] = Relationship(back_populates="players")

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(SQLModel):
    team_id: Optional[int] = None
    golfer_id: Optional[int] = None
    role: Optional[PlayerRole] = None

class PlayerRead(PlayerBase):
    id: int
    golfer: Optional[GolferRead] = None
