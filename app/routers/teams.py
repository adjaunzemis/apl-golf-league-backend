from http import HTTPStatus
from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import SQLModel, Session, select


from ..dependencies import get_session
from ..models.team import Team, TeamCreate, TeamUpdate, TeamRead
from ..models.team_golfer_link import TeamGolferLink, TeamRole
from ..models.golfer import Golfer
from ..models.flight import Flight
from ..models.flight_team_link import FlightTeamLink
from ..models.tournament import Tournament
from ..models.tournament_team_link import TournamentTeamLink
from ..models.query_helpers import TeamWithMatchData, compute_golfer_statistics_for_matches, get_flight_team_golfers_for_teams, get_matches_for_teams

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)

class TeamGolferSignupData(SQLModel):
    golfer_id: int
    golfer_name: str
    role: str
    division_id: int

class FlightTeamSignupData(SQLModel):
    flight_id: int
    name: str
    golfer_data: List[TeamGolferSignupData]

@router.get("/", response_model=List[TeamRead])
async def read_teams(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Team).offset(offset).limit(limit)).all()

@router.post("/", response_model=TeamRead)
async def create_team(*, session: Session = Depends(get_session), team: TeamCreate):
    team_db = Team.from_orm(team)
    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    return team_db

@router.get("/{team_id}", response_model=TeamWithMatchData)
async def read_team(*, session: Session = Depends(get_session), team_id: int):
    team_db = session.exec(select(Team).where(Team.id == team_id)).one_or_none()
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    team_matches = get_matches_for_teams(session=session, team_ids=(team_id,))
    team_golfers = get_flight_team_golfers_for_teams(session=session, team_ids=(team_id,))
    for golfer in team_golfers:
        golfer.statistics = compute_golfer_statistics_for_matches(golfer.golfer_id, team_matches)
    return TeamWithMatchData(
        id=team_db.id,
        name=team_db.name,
        year=team_golfers[0].year,
        golfers=team_golfers,
        matches=team_matches
    )

@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(*, session: Session = Depends(get_session), team_id: int, team: TeamUpdate):
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.dict(exclude_unset=True)
    for key, value in team_data.items():
        setattr(team_db, key, value)
    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    return team_db

@router.delete("/{team_id}")
async def delete_team(*, session: Session = Depends(get_session), team_id: int):
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")

    # Find and remove all team-golfer links
    team_golfer_links_db = session.exec(select(TeamGolferLink).where(TeamGolferLink.team_id == team_id)).all()
    for team_golfer_link_db in team_golfer_links_db:
        print(f"Deleting team-golfer link: golfer_id={team_golfer_link_db.golfer_id}")
        session.delete(team_golfer_link_db)

    # Find and remove all flight-team links
    flight_team_links_db = session.exec(select(FlightTeamLink).where(FlightTeamLink.team_id == team_id)).all()
    for flight_team_link_db in flight_team_links_db:
        print(f"Deleting flight-team link: flight_id={flight_team_link_db.flight_id}")
        session.delete(flight_team_link_db)

    # Find and remove all tournament-team links
    tournament_team_links_db = session.exec(select(TournamentTeamLink).where(TournamentTeamLink.team_id == team_id)).all()
    for tournament_team_link_db in tournament_team_links_db:
        print(f"Deleting tournament-team link: tournament_id={tournament_team_link_db.tournament_id}")
        session.delete(tournament_team_link_db)

    # Remove team
    print(f"Deleting team: id={team_db.id}")
    session.delete(team_db)

    # Commit database changes
    session.commit()
    return {"ok": True}

@router.get("/golfer-links/", response_model=List[TeamGolferLink])
async def read_team_golfer_links(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(TeamGolferLink).offset(offset).limit(limit)).all()

@router.get("/{team_id}/golfer-links/", response_model=List[TeamGolferLink])
async def read_team_golfer_links_for_team(*, session: Session = Depends(get_session), team_id: int):
    return session.exec(select(TeamGolferLink).where(TeamGolferLink.team_id == team_id)).all()

@router.post("/{team_id}/golfer-links/{golfer_id}", response_model=TeamGolferLink)
async def create_team_golfer_link(*, session: Session = Depends(get_session), team_id: int, golfer_id: int, division_id: int = Query(default=None), role: str = Query(default="Player")):
    link_db = TeamGolferLink(team_id=team_id, golfer_id=golfer_id, division_id=division_id, role=role)
    session.add(link_db)
    session.commit()
    session.refresh(link_db)
    return link_db

@router.delete("/{team_id}/golfer-links/{golfer_id}")
async def delete_team_golfer_link(*, session: Session = Depends(get_session), team_id: int, golfer_id: int):
    link_db = session.get(TeamGolferLink, [team_id, golfer_id])
    if not link_db:
        raise HTTPException(status_code=404, detail="Team-golfer link not found")
    session.delete(link_db)
    session.commit()
    return {"ok": True}

@router.post("/flight-signup", response_model=TeamRead)
async def signup_team_for_flight(*, session: Session = Depends(get_session), team_data: FlightTeamSignupData):
    # Check if the team name if valid for this flight
    team_db = session.exec(select(Team).join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id).join(Flight, onclause=Flight.id == FlightTeamLink.flight_id).where(Flight.id == team_data.flight_id).where(Team.name == team_data.name)).one_or_none()
    if team_db:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Team '{team_data.name}' already exists in flight (id={team_data.flight_id})")

    # Check for duplicate golfers in sign-up
    golfer_id_list = [team_golfer.golfer_id for team_golfer in team_data.golfer_data]
    if len(golfer_id_list) != len(set(golfer_id_list)):
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Team '{team_data.name}' contains duplicate golfer sign-ups")

    # Check if the given golfers already exist on other teams in this flight and if one captain was designated
    team_has_captain = False
    flight_golfer_ids = session.exec(select(Golfer.id).join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id).join(FlightTeamLink, onclause=FlightTeamLink.team_id == TeamGolferLink.team_id).where(FlightTeamLink.flight_id == team_data.flight_id)).all()
    for team_golfer in team_data.golfer_data:
        if team_golfer.golfer_id in flight_golfer_ids:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Golfer '{team_golfer.golfer_name}' is already on a team in flight (id={team_data.flight_id})")
        if team_golfer.role == TeamRole.CAPTAIN:
            if team_has_captain:
                raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Team '{team_data.name}' cannot have more than one captain")
            team_has_captain = True
    if not team_has_captain:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Team '{team_data.name}' must have a captain")

    # Add team to database
    team_db = Team(name=team_data.name)
    session.add(team_db)
    session.commit()

    # Add flight-team link
    flight_team_link_db = FlightTeamLink(flight_id=team_data.flight_id, team_id=team_db.id)
    session.add(flight_team_link_db)
    session.commit()

    # Add team-golfer links
    for team_golfer in team_data.golfer_data:
        team_golfer_link_db = TeamGolferLink(team_id=team_db.id, golfer_id=team_golfer.golfer_id, division_id=team_golfer.division_id, role=team_golfer.role)
        session.add(team_golfer_link_db)
        session.commit()

    return team_db
