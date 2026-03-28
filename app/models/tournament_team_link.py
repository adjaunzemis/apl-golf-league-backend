from sqlmodel import Field

from app.models.base import APLGLBase


class TournamentTeamLink(APLGLBase, table=True):
    tournament_id: int = Field(
        default=None, foreign_key="tournament.id", primary_key=True
    )
    team_id: int = Field(default=None, foreign_key="team.id", primary_key=True)
