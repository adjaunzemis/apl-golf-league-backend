from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

from app.models.flight_division_link import FlightDivisionLink
from app.models.tee import TeeGender
from app.models.tournament_division_link import TournamentDivisionLink


class DivisionBase(SQLModel):
    name: str
    gender: TeeGender
    primary_tee_id: int = Field(default=None, foreign_key="tee.id")
    secondary_tee_id: int = Field(default=None, foreign_key="tee.id")


class Division(DivisionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight: Optional["Flight"] = Relationship(
        link_model=FlightDivisionLink, sa_relationship_kwargs={"viewonly": True}
    )
    tournament: Optional["Tournament"] = Relationship(
        link_model=TournamentDivisionLink, sa_relationship_kwargs={"viewonly": True}
    )


class DivisionCreate(DivisionBase):
    id: Optional[int] = None
    pass


class DivisionUpdate(SQLModel):
    name: Optional[str] = None
    gender: Optional[TeeGender] = None
    primary_tee_id: Optional[int] = None
    secondary_tee_id: Optional[int] = None


class DivisionRead(DivisionBase):
    id: int


class DivisionData(SQLModel):
    id: int
    flight_id: int = None
    tournament_id: int = None
    name: str
    gender: str
    primary_track_id: int
    primary_track_name: str
    primary_tee_id: int
    primary_tee_name: str
    primary_tee_par: int
    primary_tee_rating: float
    primary_tee_slope: int
    secondary_track_id: int
    secondary_track_name: str
    secondary_tee_id: int
    secondary_tee_par: int
    secondary_tee_name: str
    secondary_tee_rating: float
    secondary_tee_slope: int


class FlightDivision(SQLModel):
    id: int
    flight_id: int
    name: str
    gender: str
    primary_track_id: int
    primary_track_name: str
    primary_tee_id: int
    primary_tee_name: str
    primary_tee_par: int
    primary_tee_rating: float
    primary_tee_slope: int
    secondary_track_id: int
    secondary_track_name: str
    secondary_tee_id: int
    secondary_tee_par: int
    secondary_tee_name: str
    secondary_tee_rating: float
    secondary_tee_slope: int


class TournamentDivision(SQLModel):
    id: int
    tournament_id: int
    name: str
    gender: str
    primary_track_id: int
    primary_track_name: str
    primary_tee_id: int
    primary_tee_name: str
    primary_tee_par: int
    primary_tee_rating: float
    primary_tee_slope: int
    secondary_track_id: int
    secondary_track_name: str
    secondary_tee_id: int
    secondary_tee_par: int
    secondary_tee_name: str
    secondary_tee_rating: float
    secondary_tee_slope: int
