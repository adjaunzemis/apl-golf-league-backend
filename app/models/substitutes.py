from sqlmodel import Field, Relationship, SQLModel

from app.models.flight import Flight
from app.models.golfer import Golfer


class SubstituteBase(SQLModel):
    golfer_id: int = Field(default=None, foreign_key="golfer.id", primary_key=True)
    flight_id: int = Field(default=None, foreign_key="flight.id", primary_key=True)


class Substitute(SubstituteBase, table=True):
    golfer: Golfer = Relationship()
    flight: Flight = Relationship()


class SubstituteCreate(SubstituteBase):
    pass
