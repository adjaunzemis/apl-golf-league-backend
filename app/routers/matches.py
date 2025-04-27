from datetime import datetime
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, SQLModel, select

from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.flight import Flight
from app.models.golfer import Golfer
from app.models.hole import Hole
from app.models.hole_result import HoleResult
from app.models.match import (
    Match,
    MatchCreate,
    MatchData,
    MatchDataWithCount,
    MatchRead,
    MatchUpdate,
    MatchValidationRequest,
    MatchValidationResponse,
)
from app.models.match_round_link import MatchRoundLink
from app.models.query_helpers import get_matches
from app.models.round import Round, RoundType, ScoringType
from app.models.round_golfer_link import RoundGolferLink
from app.models.team import Team
from app.models.tee import Tee
from app.models.user import User
from app.utilities import scoring
from app.utilities.apl_handicap_system import APLHandicapSystem

router = APIRouter(prefix="/matches", tags=["Matches"])


class HoleResultInput(SQLModel):
    hole_id: int
    gross_score: int


class RoundInput(SQLModel):
    team_id: int
    golfer_id: int
    golfer_playing_handicap: int
    course_id: int
    track_id: int
    tee_id: int
    holes: List[HoleResultInput]


class MatchInput(SQLModel):
    match_id: int
    flight_id: int
    week: int
    date_played: datetime
    home_score: float
    away_score: float
    rounds: List[RoundInput]


@router.get("/", response_model=MatchDataWithCount)
async def read_matches(
    *,
    session: Session = Depends(get_sql_db_session),
    team_id: int = Query(default=None, ge=0),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100),
):
    # Process query parameters to limit results
    if team_id:  # limit to specific team
        match_ids = session.exec(
            select(Match.id)
            .where(Match.home_team_id == team_id or Match.away_team_id == team_id)
            .offset(offset)
            .limit(limit)
        ).all()
    else:  # no extra limitations
        match_ids = session.exec(select(Match.id).offset(offset).limit(limit)).all()

    # Return count of relevant matches from database and match data list
    return MatchDataWithCount(
        num_matches=len(match_ids),
        matches=get_matches(session=session, match_ids=match_ids),
    )


@router.post("/", response_model=MatchRead)
async def create_match(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    match: MatchCreate,
):
    match_db = Match.model_validate(match)
    session.add(match_db)
    session.commit()
    session.refresh(match_db)
    return match_db


@router.get("/{match_id}", response_model=MatchData)
async def read_match(*, session: Session = Depends(get_sql_db_session), match_id: int):
    match_db = get_matches(session=session, match_ids=(match_id,))
    if (not match_db) or (len(match_db) != 1):
        raise HTTPException(status_code=404, detail="Match not found")
    return match_db[0]


@router.patch("/{match_id}", response_model=MatchRead)
async def update_match(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    match_id: int,
    match: MatchUpdate,
):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Match not found")
    match_data = match.model_dump(exclude_unset=True)
    for key, value in match_data.items():
        setattr(match_db, key, value)
    session.add(match_db)
    session.commit()
    session.refresh(match_db)
    return match_db


@router.delete("/{match_id}")
async def delete_match(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    match_id: int,
):
    match_db = session.get(Match, match_id)
    if not match_db:
        raise HTTPException(status_code=404, detail="Match not found")
    session.delete(match_db)
    session.commit()
    # TODO: Delete related resources (match-round-links)
    return {"ok": True}


@router.post("/rounds", response_model=MatchData)
async def post_match_rounds(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    match_input: MatchInput,
):
    # TODO: Check user credentials
    ahs = APLHandicapSystem()

    match_db = session.get(Match, match_input.match_id)
    if not match_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Match (id={match_input.match_id}) not found",
        )
    if match_db.week != match_input.week:
        raise HTTPException(
            status_code=HTTPStatus.NOT_ACCEPTABLE,
            detail=f"Match input (week={match_input.week}) does not match database (week={match_db.week})",
        )

    flight_db = session.get(Flight, match_input.flight_id)
    if not flight_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Flight (id={match_input.flight_id}) not found",
        )

    match_rounds_db = session.exec(
        select(Round)
        .join(MatchRoundLink, onclause=MatchRoundLink.round_id == Round.id)
        .where(MatchRoundLink.match_id == match_input.match_id)
    ).all()
    if len(match_rounds_db) > 0:
        raise HTTPException(
            status_code=HTTPStatus.NOT_ACCEPTABLE,
            detail=f"Rounds already submitted for match (id={match_input.match_id})",
        )

    for round_input in match_input.rounds:
        golfer_db = session.get(Golfer, round_input.golfer_id)
        if not golfer_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Golfer (id={round_input.golfer_id}) not found",
            )

        team_db = session.get(Team, round_input.team_id)
        if not team_db:
            raise HTTPException(
                status_code=HTTPStatus,
                detail=f"Team (id={round_input.team_id}) not found",
            )

        tee_db = session.get(Tee, round_input.tee_id)
        if not tee_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Tee (id={round_input.tee_id}) not found",
            )

        round_db = Round(
            tee_id=tee_db.id,
            type=RoundType.FLIGHT,
            scoring_type=ScoringType.INDIVIDUAL,
            date_played=match_input.date_played,
            date_updated=datetime.today(),
        )
        session.add(round_db)
        session.commit()
        session.refresh(round_db)

        match_round_link_db = MatchRoundLink(
            match_id=match_db.id, round_id=round_db.id, team_id=team_db.id
        )
        session.add(match_round_link_db)
        session.commit()
        session.refresh(match_round_link_db)

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

    match_db.home_score = match_input.home_score
    match_db.away_score = match_input.away_score
    session.add(match_db)
    session.commit()

    return get_matches(session=session, match_ids=(match_input.match_id,))[0]


# TODO: Add route to get hole-by-hole team handicaps


@router.post("/validate/", response_model=MatchValidationResponse)
async def validate_match(*, match: MatchValidationRequest):
    return scoring.validate_match(match)
