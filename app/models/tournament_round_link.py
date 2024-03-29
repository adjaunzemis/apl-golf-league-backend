from sqlmodel import Field, SQLModel


class TournamentRoundLink(SQLModel, table=True):
    tournament_id: int = Field(
        default=None, foreign_key="tournament.id", primary_key=True
    )
    round_id: int = Field(default=None, foreign_key="round.id", primary_key=True)
