from sqlmodel import Field, SQLModel


class Season(SQLModel, table=True):
    year: int = Field(..., description="Year for this season", primary_key=True)
    is_active: bool = Field(..., description="True if this is the active season")
