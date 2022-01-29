from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from .tee import TeeGender
from .flight_division_link import FlightDivisionLink
from .tournament_division_link import TournamentDivisionLink

class DivisionBase(SQLModel):
    name: str
    gender: TeeGender
    home_tee_id: int = Field(default=None, foreign_key="tee.id")

class Division(DivisionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight: Optional["Flight"] = Relationship(link_model=FlightDivisionLink, sa_relationship_kwargs={'viewonly': True})
    tournament: Optional["Tournament"] = Relationship(link_model=TournamentDivisionLink, sa_relationship_kwargs={'viewonly': True})

class DivisionCreate(DivisionBase):
    pass

class DivisionUpdate(SQLModel):
    name: Optional[str] = None
    gender: Optional[TeeGender] = None
    home_tee_id: Optional[int] = None

class DivisionRead(DivisionBase):
    id: int

class FlightDivisionData(SQLModel):
    division_id: int
    flight_id: int
    name: str
    gender: str
    home_tee_name: str
    home_tee_rating: float
    home_tee_slope: int

class TournamentDivisionData(SQLModel):
    division_id: int
    tournament_id: int
    name: str
    gender: str
    tee_name: str
    tee_rating: float
    tee_slope: int
