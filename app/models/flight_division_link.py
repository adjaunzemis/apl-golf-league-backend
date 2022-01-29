from sqlmodel import SQLModel, Field

class FlightDivisionLink(SQLModel, table=True):
    flight_id: int = Field(default=None, foreign_key="flight.id", primary_key=True)
    division_id: int = Field(default=None, foreign_key="division.id", primary_key=True)
