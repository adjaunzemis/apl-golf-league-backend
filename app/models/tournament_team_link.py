from sqlmodel import SQLModel, Field


class TournamentTeamLink(SQLModel, table=True):
    tournament_id: int = Field(
        default=None, foreign_key="tournament.id", primary_key=True
    )
    team_id: int = Field(default=None, foreign_key="team.id", primary_key=True)
