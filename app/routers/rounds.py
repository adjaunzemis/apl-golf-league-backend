from typing import List
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_sql_db_session
from ..models.round import (
    Round,
    RoundCreate,
    RoundData,
    RoundType,
    RoundUpdate,
    RoundRead,
    RoundReadWithData,
    RoundDataWithCount,
)
from ..models.hole_result import (
    HoleResult,
    HoleResultCreate,
    HoleResultUpdate,
    HoleResultRead,
    HoleResultReadWithHole,
)
from ..models.round_golfer_link import RoundGolferLink
from ..models.tournament import Tournament
from ..models.tournament_round_link import TournamentRoundLink
from ..models.user import User
from ..models.query_helpers import get_flight_rounds, get_tournament_rounds
from ..utilities.apl_handicap_system import APLHandicapSystem
from ..utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

router = APIRouter(prefix="/rounds", tags=["Rounds"])


@router.get("/", response_model=List[RoundData])
async def read_rounds(
    *,
    session: Session = Depends(get_sql_db_session),
    golfer_id: int = Query(default=None, ge=0),
    year: int = Query(default=None, ge=2000)
):
    # Process query parameters to limit results
    if golfer_id:  # limit by golfer
        if year:  # limit by year
            round_query_data = session.exec(
                select(Round.id, Round.type)
                .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
                .where(RoundGolferLink.golfer_id == golfer_id)
                .where(Round.date_played >= date(year, 1, 1))
                .where(Round.date_played < date(year + 1, 1, 1))
            ).all()
        else:  # all rounds for golfer
            round_query_data = session.exec(
                select(Round.id, Round.type)
                .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
                .where(RoundGolferLink.golfer_id == golfer_id)
            ).all()
    elif year:  # limit by year
        round_query_data = session.exec(
            select(Round.id, Round.type)
            .where(Round.date_played >= date(year, 1, 1))
            .where(Round.date_played < date(year + 1, 1, 1))
        ).all()
    else:  # no extra limitations
        round_query_data = session.exec(select(Round.id, Round.type)).all()
    # Return round data list
    round_data = get_flight_rounds(
        session=session,
        round_ids=(
            round_id
            for round_id, round_type in round_query_data
            if round_type == RoundType.FLIGHT
        ),
    )
    for round_id, round_type in round_query_data:
        if round_type == RoundType.TOURNAMENT:
            tournament_id = session.exec(
                select(Tournament.id)
                .join(
                    TournamentRoundLink,
                    onclause=TournamentRoundLink.tournament_id == Tournament.id,
                )
                .where(TournamentRoundLink.round_id == round_id)
            ).one()
            round_data += get_tournament_rounds(
                session=session, tournament_id=tournament_id, round_ids=(round_id,)
            )
    return round_data


@router.post("/", response_model=RoundRead)
async def create_round(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    round: RoundCreate
):
    round_db = Round.from_orm(round)
    session.add(round_db)
    session.commit()
    session.refresh(round_db)
    return round_db


@router.get("/{round_id}", response_model=RoundReadWithData)
async def read_round(*, session: Session = Depends(get_sql_db_session), round_id: int):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    return round_db


@router.patch("/{round_id}", response_model=RoundRead)
async def update_round(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    round_id: int,
    round: RoundUpdate
):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    round_data = round.dict(exclude_unset=True)
    for key, value in round_data.items():
        setattr(round_db, key, value)
    session.add(round_db)
    session.commit()
    session.refresh(round_db)
    return round_db


@router.delete("/{round_id}")
async def delete_round(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    round_id: int
):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    session.delete(round_db)
    session.commit()
    # TODO: Delete related resources (match-round-links, round-golfer-links, hole results, etc.)
    return {"ok": True}


@router.get("/hole_results/", response_model=List[HoleResultRead])
async def read_hole_results(
    *,
    session: Session = Depends(get_sql_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100)
):
    return session.exec(select(HoleResult).offset(offset).limit(limit)).all()


@router.post("/hole_results/", response_model=HoleResultRead)
async def create_hole_result(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    hole_result: HoleResultCreate
):
    hole_result_db = HoleResult.from_orm(hole_result)
    session.add(hole_result_db)
    session.commit()
    session.refresh(hole_result_db)
    return hole_result_db


@router.get("/hole_results/{hole_result_id}", response_model=HoleResultReadWithHole)
async def read_hole_result(
    *, session: Session = Depends(get_sql_db_session), hole_result_id: int
):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    return hole_result_db


@router.patch("/hole_results/{hole_result_id}", response_model=HoleResultRead)
async def update_hole_result(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    hole_result_id: int,
    hole_result: HoleResultUpdate
):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    round_data = hole_result.dict(exclude_unset=True)
    for key, value in round_data.items():
        setattr(hole_result_db, key, value)
    session.add(hole_result_db)
    session.commit()
    session.refresh(hole_result_db)
    return hole_result_db


@router.delete("/hole_results/{hole_result_id}")
async def delete_hole_result(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    hole_result_id: int
):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    session.delete(hole_result_db)
    session.commit()
    return {"ok": True}


class HoleResultValidationRequest(BaseModel):
    number: int
    par: int
    stroke_index: int
    gross_score: int


class HoleResultValidationResponse(HoleResultValidationRequest):
    handicap_strokes: int
    adjusted_gross_score: int
    net_score: int
    max_gross_score: int
    is_valid: bool = False


class RoundValidationRequest(BaseModel):
    date_played: datetime
    course_handicap: int
    holes: List[HoleResultValidationRequest] = []


class RoundValidationResponse(BaseModel):
    date_played: datetime
    course_handicap: int
    holes: List[HoleResultValidationResponse] = []
    is_valid: bool = False


@router.post("/validate/", response_model=RoundValidationResponse)
async def validate_round(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    round: RoundValidationRequest
):
    # Determine handicapping system
    if round.date_played.year >= 2022:
        ahs = APLHandicapSystem()
    else:
        ahs = APLLegacyHandicapSystem()

    # Prepare round response
    round_response = RoundValidationResponse(
        date_played=round.date_played, course_handicap=round.course_handicap
    )

    for hole in round.holes:
        # Initialize hole response with hole request data
        hole_response = HoleResultValidationResponse()
        hole_response.number = hole.number
        hole_response.par = hole.par
        hole_response.stroke_index = hole.stroke_index
        hole_response.gross_score = hole.gross_score

        # Compute handicapping scores for this hole
        hole_response.handicap_strokes = ahs.compute_hole_handicap_strokes(
            hole.stroke_index, round.course_handicap
        )
        hole_response.adjusted_gross_score = ahs.compute_hole_adjusted_gross_score(
            hole.par, hole.stroke_index, hole.gross_score, round.course_handicap
        )
        hole_response.net_score = hole.gross_score - hole_response.handicap_strokes
        hole_response.max_gross_score = ahs.compute_hole_maximum_strokes(
            hole.par, hole_response.handicap_strokes
        )

        # Check validity for this hole
        hole_response.is_valid = (
            hole_response.gross_score > 0
            and hole_response.gross_score <= hole_response.max_gross_score
        )

        # Add hole to round response
        round_response.holes.append(hole_response)

    # Check validity for this round
    round_response.is_valid = any([not hole.is_valid for hole in round_response.holes])

    # Return round response
    return round_response
