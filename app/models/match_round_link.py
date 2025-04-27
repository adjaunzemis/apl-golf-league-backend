from sqlmodel import Field, SQLModel


class MatchRoundLink(SQLModel, table=True):
    match_id: int = Field(..., foreign_key="match.id", primary_key=True)
    round_id: int = Field(..., foreign_key="round.id", primary_key=True)
    team_id: int = Field(..., foreign_key="team.id")
