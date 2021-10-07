from typing import List, Optional
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

class GolferAffiliation(str, Enum):
    APL_EMPLOYEE = "APL_EMPLOYEE"
    APL_RETIREE = "APL_RETIREE"
    APL_FAMILY = "APL_FAMILY"
    NON_APL_EMPLOYEE = "NON_APL_EMPLOYEE"

class GolferBase(SQLModel):
    name: str
    affiliation: Optional[GolferAffiliation] = None

class Golfer(GolferBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class GolferCreate(GolferBase):
    pass

class GolferUpdate(SQLModel):
    name: Optional[str] = None
    affiliation: Optional[GolferAffiliation] = None

class GolferRead(GolferBase):
    id: int
