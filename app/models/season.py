from sqlmodel import Field

from app.models.base import APLGLBase


class Season(APLGLBase, table=True):
    year: int = Field(..., description="Year for this season", primary_key=True)
    is_active: bool = Field(False, description="True if this is the active season")


class SeasonCreate(APLGLBase):
    year: int = Field(..., description="Year for this season")
