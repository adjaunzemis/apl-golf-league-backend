from sqlmodel import SQLModel, Field


class MatchRoundLink(SQLModel, table=True):
    match_id: int = Field(default=None, foreign_key="match.id", primary_key=True)
    round_id: int = Field(default=None, foreign_key="round.id", primary_key=True)
