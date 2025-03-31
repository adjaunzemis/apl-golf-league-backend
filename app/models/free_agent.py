from enum import StrEnum

from sqlmodel import Field, Relationship, SQLModel

from app.models.division import Division
from app.models.flight import Flight
from app.models.golfer import Golfer


class FreeAgentCadence(StrEnum):
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    OCCASIONALLY = "Occasionally"


class FreeAgentBase(SQLModel):
    golfer_id: int = Field(foreign_key="golfer.id", primary_key=True)
    flight_id: int = Field(foreign_key="flight.id", primary_key=True)
    division_id: int = Field(foreign_key="division.id")
    cadence: FreeAgentCadence


class FreeAgent(FreeAgentBase, table=True):
    golfer: Golfer = Relationship()
    flight: Flight = Relationship()
    division: Division = Relationship()


class FreeAgentCreate(FreeAgentBase):
    pass
