from sqlmodel import Field

from app.models.base import APLGLBaseModel


class MatchRoundLink(APLGLBaseModel, table=True):
    match_id: int = Field(..., foreign_key="match.id", primary_key=True)
    round_id: int = Field(..., foreign_key="round.id", primary_key=True)
    team_id: int = Field(..., foreign_key="team.id")
