from sqlmodel import Field

from app.models.base import APLGLBaseModel


class Season(APLGLBaseModel, table=True):
    year: int = Field(..., description="Year for this season", primary_key=True)
    is_active: bool = Field(False, description="True if this is the active season")


class SeasonCreate(APLGLBaseModel):
    year: int = Field(..., description="Year for this season")
