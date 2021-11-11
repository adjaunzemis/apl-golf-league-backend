from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select, SQLModel

from ..dependencies import get_session
from ..models.golfer import Golfer, GolferCreate, GolferUpdate, GolferRead
from ..models.player import Player, PlayerData
from ..models.team import Team
from ..models.division import Division
from ..models.flight import Flight

router = APIRouter(
    prefix="/golfers",
    tags=["Golfers"]
)

class GolferData(SQLModel):
    golfer_id: int
    name: str
    affiliation: str
    player_data: List[PlayerData] = []

class GolferDataWithCount(SQLModel):
    num_golfers: int
    golfers: List[GolferData]

@router.get("/", response_model=GolferDataWithCount)
async def read_golfers(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # TODO: Process query parameters to further limit golfer results returned from database
    num_golfers = len(session.exec(select(Golfer.id)).all())
    golfer_query_data = session.exec(select(Golfer).offset(offset).limit(limit))

    # Reformat golfer data
    if num_golfers == 0:
        return GolferDataWithCount(num_golfers=0, golfers=[])
    
    golfer_data = [GolferData(
        golfer_id=golfer.id,
        name=golfer.name,
        affiliation=golfer.affiliation
    ) for golfer in golfer_query_data]
    golfer_ids = [g.golfer_id for g in golfer_data]

    # Query player data for selected golfers
    player_query_data = session.exec(select(Player, Team, Golfer, Division).join(Team).join(Golfer).join(Division).where(Player.golfer_id.in_(golfer_ids)))
    player_data = [PlayerData(
        player_id=player.id,
        team_id=player.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        division_name=division.name,
        team_name=team.name,
        role=player.role
    ) for player, team, golfer, division in player_query_data]

    # Add player data to golfer data
    for g in golfer_data:
        g.player_data = [p for p in player_data if p.golfer_id == g.golfer_id]

    # Return count of relevant golfers from database and golfer data list
    return GolferDataWithCount(num_golfers=num_golfers, golfers=golfer_data)

@router.post("/", response_model=GolferRead)
async def create_golfer(*, session: Session = Depends(get_session), golfer: GolferCreate):
    golfer_db = Golfer.from_orm(golfer)
    session.add(golfer_db)
    session.commit()
    session.refresh(golfer_db)
    return golfer_db

@router.get("/{golfer_id}", response_model=GolferRead)
async def read_golfer(*, session: Session = Depends(get_session), golfer_id: int):
    golfer_db = session.get(Golfer, golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=404, detail="Golfer not found")
    return golfer_db

@router.patch("/{golfer_id}", response_model=GolferRead)
async def update_golfer(*, session: Session = Depends(get_session), golfer_id: int, golfer: GolferUpdate):
    golfer_db = session.get(Golfer, golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=404, detail="Golfer not found")
    golfer_data = golfer.dict(exclude_unset=True)
    for key, value in golfer_data.items():
        setattr(golfer_db, key, value)
    session.add(golfer_db)
    session.commit()
    session.refresh(golfer_db)
    return golfer_db

@router.delete("/{golfer_id}")
async def delete_golfer(*, session: Session = Depends(get_session), golfer_id: int):
    golfer_db = session.get(Golfer, golfer_id)
    if not golfer_db:
        raise HTTPException(status_code=404, detail="Golfer not found")
    session.delete(golfer_db)
    session.commit()
    return {"ok": True}
