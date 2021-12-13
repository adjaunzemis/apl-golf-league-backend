from typing import List, Optional
from enum import Enum
from sqlalchemy.orm.relationships import foreign
from sqlmodel import SQLModel, Field, Relationship

from .golfer import Golfer, GolferRead
from .division import Division, DivisionRead

class PlayerRole(str, Enum):
    CAPTAIN = "CAPTAIN"
    PLAYER = "PLAYER"
    SUBSTITUTE = "SUBSTITUTE"

class PlayerBase(SQLModel):
    team_id: int = Field(default=None, foreign_key="team.id")
    golfer_id: int = Field(default=None, foreign_key="golfer.id")
    division_id: int = Field(default=None, foreign_key="division.id")
    role: Optional[PlayerRole] = None

class Player(PlayerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team: Optional["Team"] = Relationship(back_populates="players")
    golfer: Golfer = Relationship()
    division: Division = Relationship()

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(SQLModel):
    team_id: Optional[int] = None
    golfer_id: Optional[int] = None
    division_id: Optional[int] = None
    role: Optional[PlayerRole] = None

class PlayerRead(PlayerBase):
    id: int

class PlayerReadWithData(PlayerRead):
    golfer: Optional[GolferRead] = None
    division: Optional[DivisionRead] = None

class PlayerData(SQLModel):
    player_id: int
    team_id: int
    golfer_id: int
    golfer_name: str
    division_name: str
    flight_name: str
    team_name: str
    role: str
