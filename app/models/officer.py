from enum import StrEnum
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel


class Committee(StrEnum):
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
    committee: Committee = Field(
        sa_column=Column(
            SAEnum(
                Committee,
                name="committee_enum",
                native_enum=True,
                create_constraint=True,
            ),
            nullable=False,
        )
    )
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
