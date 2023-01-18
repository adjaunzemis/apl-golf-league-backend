from sqlmodel import SQLModel, Field


class TournamentDivisionLink(SQLModel, table=True):
    tournament_id: int = Field(
        default=None, foreign_key="tournament.id", primary_key=True
    )
    division_id: int = Field(default=None, foreign_key="division.id", primary_key=True)
