from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class GolferBase(SQLModel):
    name: str
    affiliation: Optional[str] = None

class Golfer(GolferBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class GolferCreate(GolferBase):
    pass

class GolferUpdate(SQLModel):
    name: Optional[str] = None
    affiliation: Optional[str] = None

class GolferRead(GolferBase):
    id: int
