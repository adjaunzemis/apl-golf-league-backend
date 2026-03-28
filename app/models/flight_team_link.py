from sqlmodel import Field

from app.models.base import APLGLBase


class FlightTeamLink(APLGLBase, table=True):
    flight_id: int = Field(default=None, foreign_key="flight.id", primary_key=True)
    team_id: int = Field(default=None, foreign_key="team.id", primary_key=True)
