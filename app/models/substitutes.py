from sqlmodel import Field, Relationship, SQLModel

from app.models.division import Division
from app.models.flight import Flight
from app.models.golfer import Golfer


class SubstituteBase(SQLModel):
    golfer_id: int = Field(foreign_key="golfer.id", primary_key=True)
    flight_id: int = Field(foreign_key="flight.id", primary_key=True)
    division_id: int = Field(foreign_key="division.id")


class Substitute(SubstituteBase, table=True):
    golfer: Golfer = Relationship()
    flight: Flight = Relationship()
    division: Division = Relationship()


class SubstituteCreate(SubstituteBase):
    pass
