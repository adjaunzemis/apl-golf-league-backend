from sqlmodel import Field

from app.models.base import APLGLBaseModel


class TournamentTeamLink(APLGLBaseModel, table=True):
    tournament_id: int = Field(
        default=None, foreign_key="tournament.id", primary_key=True
    )
    team_id: int = Field(default=None, foreign_key="team.id", primary_key=True)
