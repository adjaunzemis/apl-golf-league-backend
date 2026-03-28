from sqlmodel import Field

from app.models.base import APLGLBaseModel


class TournamentRoundLink(APLGLBaseModel, table=True):
    tournament_id: int = Field(
        default=None, foreign_key="tournament.id", primary_key=True
    )
    round_id: int = Field(default=None, foreign_key="round.id", primary_key=True)
