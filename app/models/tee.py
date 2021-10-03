from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class TeeBase(SQLModel):
    name: str
    track_id: Optional[int] = Field(default=None, foreign_key="track.id")

class Tee(TeeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    track: Optional["Track"] = Relationship(back_populates="tees")

class TeeCreate(TeeBase):
    pass

class TeeUpdate(SQLModel):
    name: Optional[str] = None
    track_id: Optional[int] = None

class TeeRead(TeeBase):
    id: int

# TODO: TeeReadWithHoles
