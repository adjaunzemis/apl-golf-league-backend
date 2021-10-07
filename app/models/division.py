from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from ..models.tee import TeeGender

class DivisionBase(SQLModel):
    name: str
    gender: TeeGender
    flight_id: int = Field(default=None, foreign_key="flight.id")
    home_tee_id: int = Field(default=None, foreign_key="tee.id")

class Division(DivisionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    flight: Optional["Flight"] = Relationship(back_populates="divisions")

class DivisionCreate(DivisionBase):
    pass

class DivisionUpdate(SQLModel):
    name: Optional[str] = None
    gender: Optional[TeeGender] = None
    flight_id: Optional[int] = None
    home_tee_id: Optional[int] = None

class DivisionRead(DivisionBase):
    id: int
