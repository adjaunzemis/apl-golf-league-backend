from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import SQLModel, Session, select
from http import HTTPStatus


from .matches import RoundInput
from ..dependencies import get_current_active_user, get_session
from ..models.tournament import Tournament, TournamentCreate, TournamentUpdate, TournamentRead
from ..models.tournament_round_link import TournamentRoundLink
from ..models.tournament_team_link import TournamentTeamLink
from ..models.round_golfer_link import RoundGolferLink
from ..models.golfer import Golfer
from ..models.team import Team
from ..models.round import Round, RoundSummary, RoundType, ScoringType
from ..models.tee import Tee
from ..models.hole import Hole
from ..models.hole_result import HoleResult
from ..models.user import User
from ..models.query_helpers import TournamentData, TournamentInfoWithCount, get_round_summaries, get_rounds_for_tournament, get_tournaments, get_divisions_in_tournaments, get_teams_in_tournaments
from ..utilities.apl_handicap_system import APLHandicapSystem

router = APIRouter(
    prefix="/tournaments",
    tags=["Tournaments"]
)

class TournamentRoundsInput(SQLModel):
    tournament_id: int
    date_played: datetime
    rounds: List[RoundInput]

@router.get("/", response_model=TournamentInfoWithCount)
async def read_tournaments(*, session: Session = Depends(get_session), year: int = Query(default=None, ge=2000)):
    if year: # filter to a certain year
        tournament_ids = session.exec(select(Tournament.id).where(Tournament.year == year)).all()
    else: # get all
        tournament_ids = session.exec(select(Tournament.id)).all()
    tournament_info = get_tournaments(session=session, tournament_ids=tournament_ids)
    return TournamentInfoWithCount(num_tournaments=len(tournament_ids), tournaments=tournament_info)

@router.post("/", response_model=TournamentRead)
async def create_tournament(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), tournament: TournamentCreate):
    tournament_db = Tournament.from_orm(tournament)
    session.add(tournament_db)
    session.commit()
    session.refresh(tournament_db)
    return tournament_db

@router.get("/{tournament_id}", response_model=TournamentData)
async def read_tournament(*, session: Session = Depends(get_session), tournament_id: int):
    # Query database for selected tournament, error if not found
    tournament_data = get_tournaments(session=session, tournament_ids=(tournament_id,))
    if (not tournament_data) or (len(tournament_data) == 0):
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament_data = tournament_data[0]
    # Add division and team data to selected tournament
    tournament_data.divisions = get_divisions_in_tournaments(session=session, tournament_ids=(tournament_id,))
    tournament_data.teams = get_teams_in_tournaments(session=session, tournament_ids=(tournament_id,))
    # Compile round data and add to selected tournament teams
    round_data = get_rounds_for_tournament(session=session, tournament_id=tournament_id)
    for team in tournament_data.teams:
        team.rounds = [round for round in round_data if round.team_id == team.id]
    return tournament_data

@router.patch("/{tournament_id}", response_model=TournamentRead)
async def update_tournament(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), tournament_id: int, tournament: TournamentUpdate):
    tournament_db = session.get(Tournament, tournament_id)
    if not tournament_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament_data = tournament.dict(exclude_unset=True)
    for key, value in tournament_data.items():
        setattr(tournament_db, key, value)
    session.add(tournament_db)
    session.commit()
    session.refresh(tournament_db)
    return tournament_db

@router.delete("/{tournament_id}")
async def delete_tournament(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), tournament_id: int):
    tournament_db = session.get(Tournament, tournament_id)
    if not tournament_db:
        raise HTTPException(status_code=404, detail="Tournament not found")
    session.delete(tournament_db)
    session.commit()
    return {"ok": True}

@router.post("/rounds", response_model=List[RoundSummary])
async def post_tournament_rounds(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), rounds_input: TournamentRoundsInput):
    # TODO: Check user credentials
    ahs = APLHandicapSystem()
    tournament_db = session.get(Tournament, rounds_input.tournament_id)
    if not tournament_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Tournament (id={rounds_input.tournament_id}) not found")
    if tournament_db.locked:
        raise HTTPException(status_code=HTTPStatus.NOT_ACCEPTABLE, detail=f"Tournament '{tournament_db.name} ({tournament_db.year})' is locked")
    if len(tournament_rounds_db) > 0:
        raise HTTPException(status_code=HTTPStatus.NOT_ACCEPTABLE, detail=f"Rounds already submitted for team (id={rounds_input.team_id}) in tournament (id={rounds_input.tournament_id})")
    round_ids = []
    for round_input in rounds_input.rounds:
        golfer_db = session.get(Golfer, round_input.golfer_id)
        if not golfer_db:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Golfer (id={round_input.golfer_id}) not found")
        team_db = session.get(Team, round_input.team_id)
        tournament_rounds_db = session.exec(select(Round).join(TournamentRoundLink, onclause=TournamentRoundLink.round_id == Round.id).join(TournamentTeamLink, onclause=TournamentTeamLink.tournament_id == TournamentRoundLink.tournament_id).where(TournamentRoundLink.tournament_id == rounds_input.tournament_id).where(TournamentTeamLink.team_id == round_input.team_id)).all()
        if len(tournament_rounds_db) > 0:
            raise HTTPException(status_code=HTTPStatus.NOT_ACCEPTABLE, detail=f"Rounds already submitted for team (id={rounds_input.team_id}) in tournament (id={rounds_input.tournament_id})")
        if not team_db:
            raise HTTPException(status_code=HTTPStatus, detail=f"Team (id={round_input.team_id}) not found")
        tee_db = session.get(Tee, round_input.tee_id)
        if not tee_db:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Tee (id={round_input.tee_id}) not found")
        round_db = Round(
            tee_id=tee_db.id,
            type=RoundType.TOURNAMENT,
            scoring_type=ScoringType.GROUP,
            date_played=rounds_input.date_played,
            date_updated=datetime.today()
        )
        session.add(round_db)
        session.commit()
        session.refresh(round_db)
        round_ids.append(round_db.id)
        tournament_round_link_db = TournamentRoundLink(
            tournament_id=tournament_db.id,
            round_id=round_db.id
        )
        session.add(tournament_round_link_db)
        session.commit()
        session.refresh(tournament_round_link_db)
        round_golfer_link_db = RoundGolferLink(
            round_id=round_db.id,
            golfer_id=golfer_db.id,
            playing_handicap=round_input.golfer_playing_handicap
        )
        session.add(round_golfer_link_db)
        session.commit()
        session.refresh(round_golfer_link_db)
        for hole_result_input in round_input.holes:
            hole_db = session.get(Hole, hole_result_input.hole_id)
            if not hole_db:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Hole (id={hole_result_input.hole_id}) not found")
            handicap_strokes = ahs.compute_hole_handicap_strokes(hole_db.stroke_index, round_input.golfer_playing_handicap)
            hole_result_db = HoleResult(
                round_id=round_db.id,
                hole_id=hole_result_input.hole_id,
                handicap_strokes=handicap_strokes,
                gross_score=hole_result_input.gross_score,
                adjusted_gross_score=ahs.compute_hole_adjusted_gross_score(
                    par=hole_db.par,
                    stroke_index=hole_db.stroke_index,
                    score=hole_result_input.gross_score,
                    course_handicap=round_input.golfer_playing_handicap
                ),
                net_score=(hole_result_input.gross_score - handicap_strokes)
            )
            session.add(hole_result_db)
        session.commit()
    return get_round_summaries(session=session, round_ids=round_ids)[0] # TODO: clean up implementation of response
