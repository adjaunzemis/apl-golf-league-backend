from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, Path, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, SQLModel, select

from app.database import tournaments as db_tournaments
from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.golfer import Golfer
from app.models.hole import Hole
from app.models.hole_result import HoleResult
from app.models.query_helpers import (
    TournamentData,
    get_divisions_in_tournaments,
    get_round_summaries,
    get_rounds_for_tournament,
    get_teams_in_tournaments,
    get_tournaments,
)
from app.models.round import Round, RoundSummary, RoundType, ScoringType
from app.models.round_golfer_link import RoundGolferLink
from app.models.team import Team
from app.models.tee import Tee
from app.models.tournament import (
    Tournament,
    TournamentCreate,
    TournamentInfo,
    TournamentRead,
)
from app.models.tournament_division_link import TournamentDivisionLink
from app.models.tournament_round_link import TournamentRoundLink
from app.models.tournament_team_link import TournamentTeamLink
from app.models.user import User
from app.routers.matches import RoundInput
from app.routers.utilities import upsert_division
from app.utilities.apl_handicap_system import APLHandicapSystem

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


class TournamentInput(SQLModel):
    tournament_id: int
    date_played: datetime
    rounds: list[RoundInput]


@router.get("/", response_model=list[TournamentInfo])
async def read_tournaments(
    *,
    session: Session = Depends(get_sql_db_session),
    year: int = Query(default=None, ge=2000),
):
    tournament_ids = db_tournaments.get_ids(session=session, year=year)
    tournaments = [
        db_tournaments.get_info(session=session, tournament_id=tournament_id)
        for tournament_id in tournament_ids
    ]
    return sorted(tournaments, key=lambda t: t.date)


@router.get("/{tournament_id}", response_model=TournamentData)
async def read_tournament(
    *, session: Session = Depends(get_sql_db_session), tournament_id: int
):
    # Query database for selected tournament, error if not found
    tournament_data = get_tournaments(session=session, tournament_ids=(tournament_id,))
    if (not tournament_data) or (len(tournament_data) == 0):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Tournament not found"
        )
    tournament_data = tournament_data[0]
    # Add division and team data to selected tournament
    tournament_data.divisions = get_divisions_in_tournaments(
        session=session, tournament_ids=(tournament_id,)
    )
    tournament_data.teams = get_teams_in_tournaments(
        session=session, tournament_ids=(tournament_id,)
    )
    # Compile round data and add to selected tournament teams
    round_data = get_rounds_for_tournament(session=session, tournament_id=tournament_id)
    for team in tournament_data.teams:
        team.rounds = [round for round in round_data if round.team_id == team.id]
    return tournament_data


@router.post("/", response_model=TournamentRead)
async def create_tournament(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    tournament: TournamentCreate,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to create tournaments",
        )

    # TODO: Validate tournament data (e.g. division tees against tournament course tees)

    return upsert_tournament(session=session, tournament_data=tournament)


@router.put("/{tournament_id}", response_model=TournamentRead)
async def update_tournament(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    tournament_id: int,
    tournament: TournamentCreate,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to update tournaments",
        )

    tournament_db = session.get(Tournament, tournament_id)
    if not tournament_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Tournament not found"
        )

    # TODO: Validate tournament data (e.g. division tees against tournament course tees)

    return upsert_tournament(session=session, tournament_data=tournament)


@router.delete("/{tournament_id}")
async def delete_tournament(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    tournament_id: int,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to create tournaments",
        )

    tournament_db = session.get(Tournament, tournament_id)
    if not tournament_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Tournament not found"
        )
    session.delete(tournament_db)
    session.commit()
    return {"ok": True}


@router.post("/rounds", response_model=list[RoundSummary])
async def post_tournament_rounds(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    tournament_input: TournamentInput,
):
    # TODO: Check user credentials
    ahs = APLHandicapSystem()
    tournament_db = session.get(Tournament, tournament_input.tournament_id)
    if not tournament_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Tournament (id={tournament_input.tournament_id}) not found",
        )
    if tournament_db.locked:
        raise HTTPException(
            status_code=HTTPStatus.NOT_ACCEPTABLE,
            detail=f"Tournament '{tournament_db.name} ({tournament_db.year})' is locked",
        )

    round_ids = []
    for round_input in tournament_input.rounds:
        golfer_db = session.get(Golfer, round_input.golfer_id)
        if not golfer_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Golfer (id={round_input.golfer_id}) not found",
            )
        team_db = session.get(Team, round_input.team_id)
        if not team_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Team (id={round_input.team_id}) not found",
            )
        tee_db = session.get(Tee, round_input.tee_id)
        if not tee_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Tee (id={round_input.tee_id}) not found",
            )
        tournament_rounds_db = session.exec(
            select(Round)
            .join(
                TournamentRoundLink, onclause=TournamentRoundLink.round_id == Round.id
            )
            .join(
                TournamentTeamLink,
                onclause=TournamentTeamLink.tournament_id
                == TournamentRoundLink.tournament_id,
            )
            .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
            .where(TournamentRoundLink.tournament_id == tournament_db.id)
            .where(TournamentTeamLink.team_id == team_db.id)
            .where(RoundGolferLink.golfer_id == golfer_db.id)
            .where(Round.tee_id == tee_db.id)
        ).all()
        if (not tournament_rounds_db) or (len(tournament_rounds_db) == 0):
            round_db = Round(
                tee_id=tee_db.id,
                type=RoundType.TOURNAMENT,
                scoring_type=(
                    ScoringType.INDIVIDUAL
                    if tournament_db.individual
                    else ScoringType.GROUP
                ),
                date_played=tournament_input.date_played,
                date_updated=datetime.today(),
            )
            session.add(round_db)
            session.commit()
            session.refresh(round_db)
            round_ids.append(round_db.id)

            tournament_round_link_db = TournamentRoundLink(
                tournament_id=tournament_db.id, round_id=round_db.id
            )
            session.add(tournament_round_link_db)
            session.commit()
            session.refresh(tournament_round_link_db)

            round_golfer_link_db = RoundGolferLink(
                round_id=round_db.id,
                golfer_id=golfer_db.id,
                playing_handicap=round_input.golfer_playing_handicap,
            )
            session.add(round_golfer_link_db)
            session.commit()
            session.refresh(round_golfer_link_db)

            for hole_result_input in round_input.holes:
                hole_db = session.get(Hole, hole_result_input.hole_id)
                if not hole_db:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f"Hole (id={hole_result_input.hole_id}) not found",
                    )
                handicap_strokes = ahs.compute_hole_handicap_strokes(
                    hole_db.stroke_index, round_input.golfer_playing_handicap
                )
                hole_result_db = HoleResult(
                    round_id=round_db.id,
                    hole_id=hole_result_input.hole_id,
                    handicap_strokes=handicap_strokes,
                    gross_score=hole_result_input.gross_score,
                    adjusted_gross_score=ahs.compute_hole_adjusted_gross_score(
                        par=hole_db.par,
                        stroke_index=hole_db.stroke_index,
                        score=hole_result_input.gross_score,
                        course_handicap=round_input.golfer_playing_handicap,
                    ),
                    net_score=(hole_result_input.gross_score - handicap_strokes),
                )
                session.add(hole_result_db)
            session.commit()

    return get_round_summaries(
        session=session, round_ids=round_ids
    )  # TODO: clean up implementation of response


def upsert_tournament(
    *, session: Session, tournament_data: TournamentCreate
) -> TournamentRead:
    """Updates/inserts a tournament data record."""
    if tournament_data.id is None:  # create new tournament
        tournament_db = Tournament.model_validate(tournament_data)
    else:  # update existing tournament
        tournament_db = session.get(Tournament, tournament_data.id)
        if not tournament_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Tournament (id={tournament_data.id}) not found",
            )
        tournament_dict = tournament_data.model_dump(exclude_unset=True)
        for key, value in tournament_dict.items():
            if key != "divisions":
                setattr(tournament_db, key, value)
    session.add(tournament_db)
    session.commit()
    session.refresh(tournament_db)

    for division in tournament_data.divisions:
        division_db = upsert_division(session=session, division_data=division)

        # Create tournament-division link (if needed)
        tournament_division_link_db = session.exec(
            select(TournamentDivisionLink)
            .where(TournamentDivisionLink.tournament_id == tournament_db.id)
            .where(TournamentDivisionLink.division_id == division_db.id)
        ).one_or_none()
        if not tournament_division_link_db:
            tournament_division_link_db = TournamentDivisionLink(
                tournament_id=tournament_db.id, division_id=division_db.id
            )
            session.add(tournament_division_link_db)
            session.commit()
            session.refresh(tournament_division_link_db)

    session.refresh(tournament_db)
    return tournament_db


@router.get("/info/{tournament_id}")
async def get_info(
    *,
    session: Session = Depends(get_sql_db_session),
    tournament_id: int = Path(..., description="Tournament identifier"),
):
    return db_tournaments.get_info(session=session, tournament_id=tournament_id)


@router.get("/divisions/{tournament_id}")
async def get_divisions(
    *,
    session: Session = Depends(get_sql_db_session),
    tournament_id: int = Path(..., description="Tournament identifier"),
):
    return db_tournaments.get_divisions(session=session, tournament_id=tournament_id)


@router.get("/teams/{tournament_id}")
async def get_teams(
    *,
    session: Session = Depends(get_sql_db_session),
    tournament_id: int = Path(..., description="Tournament identifier"),
):
    return db_tournaments.get_teams(session=session, tournament_id=tournament_id)


@router.get("/free-agents/{tournament_id}")
async def get_free_agents(
    *,
    session: Session = Depends(get_sql_db_session),
    tournament_id: int = Path(..., description="Tournament identifier"),
):
    return db_tournaments.get_free_agents(session=session, tournament_id=tournament_id)


@router.get("/rounds/{tournament_id}")
async def get_rounds(
    *,
    session: Session = Depends(get_sql_db_session),
    tournament_id: int = Path(..., description="Tournament identifier"),
):
    return db_tournaments.get_round_summaries(
        session=session, tournament_id=tournament_id
    )


@router.get("/team-rounds/{team_id}")
async def get_rounds_for_team(
    *,
    session: Session = Depends(get_sql_db_session),
    team_id: int = Path(..., description="Team identifier"),
):
    return db_tournaments.get_rounds_for_team(session=session, team_id=team_id)


@router.get("/standings/{tournament_id}")
async def get_standings(
    *,
    session: Session = Depends(get_sql_db_session),
    tournament_id: int = Path(..., description="Tournament identifier"),
):
    return db_tournaments.get_standings(session=session, tournament_id=tournament_id)


@router.get("/statistics/{tournament_id}")
async def get_statistics(
    *,
    session: Session = Depends(get_sql_db_session),
    tournament_id: int = Path(..., description="Tournament identifier"),
):
    return db_tournaments.get_statistics(session=session, tournament_id=tournament_id)
