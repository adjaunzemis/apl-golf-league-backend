from typing import Optional
from sqlmodel import SQLModel, Field


class RoundGolferLink(SQLModel, table=True):
    round_id: int = Field(default=None, foreign_key="round.id", primary_key=True)
    golfer_id: int = Field(default=None, foreign_key="golfer.id", primary_key=True)
    playing_handicap: Optional[int] = None
