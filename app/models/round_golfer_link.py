from typing import Optional

from sqlmodel import Field

from app.models.base import APLGLBaseModel


class RoundGolferLink(APLGLBaseModel, table=True):
    round_id: int = Field(default=None, foreign_key="round.id", primary_key=True)
    golfer_id: int = Field(default=None, foreign_key="golfer.id", primary_key=True)
    playing_handicap: Optional[int] = None
