from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class Committee(str, Enum):
    LEAGUE = "LEAGUE"
    EXECUTIVE = "EXECUTIVE"
    RULES = "RULES"
    TOURNAMENT = "TOURNAMENT"
    BANQUET_AND_AWARDS = "BANQUET_AND_AWARDS"
    PUBLICITY = "PUBLICITY"
    PLANNING = "PLANNING"


class OfficerBase(SQLModel):
    name: str
    year: int
    committee: Committee
    role: str
    email: Optional[str]
    phone: Optional[str]


class Officer(OfficerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class OfficerCreate(OfficerBase):
    pass


class OfficerUpdate(SQLModel):
    name: Optional[str] = None
    year: Optional[int] = None
    committee: Optional[Committee] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class OfficerRead(OfficerBase):
    id: int
