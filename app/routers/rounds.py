from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Depends, Query, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from app.dependencies import get_current_active_user, get_sql_db_session
from app.models.golfer import Golfer
from app.models.hole import Hole
from app.models.hole_result import (
    HoleResult,
    HoleResultCreate,
    HoleResultRead,
    HoleResultReadWithHole,
    HoleResultSubmissionResponse,
    HoleResultUpdate,
)
from app.models.query_helpers import get_flight_rounds, get_tournament_rounds
from app.models.round import (
    Round,
    RoundCreate,
    RoundRead,
    RoundReadWithData,
    RoundResults,
    RoundSubmissionRequest,
    RoundSubmissionResponse,
    RoundType,
    RoundUpdate,
    RoundValidationRequest,
    RoundValidationResponse,
)
from app.models.round_golfer_link import RoundGolferLink
from app.models.tournament import Tournament
from app.models.tournament_round_link import TournamentRoundLink
from app.models.user import User
from app.utilities import scoring

router = APIRouter(prefix="/rounds", tags=["Rounds"])


@router.get("/", response_model=List[RoundResults])
async def read_rounds(
    *,
    session: Session = Depends(get_sql_db_session),
    golfer_id: int = Query(default=None, ge=0),
    year: int = Query(default=None, ge=2000),
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
    round: RoundCreate,
):
    round_db = Round.model_validate(round)
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
    round: RoundUpdate,
):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    round_data = round.model_dump(exclude_unset=True)
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
    round_id: int,
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
    limit: int = Query(default=100, le=100),
):
    return session.exec(select(HoleResult).offset(offset).limit(limit)).all()


@router.post("/hole_results/", response_model=HoleResultRead)
async def create_hole_result(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    hole_result: HoleResultCreate,
):
    hole_result_db = HoleResult.model_validate(hole_result)
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
    hole_result: HoleResultUpdate,
):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    round_data = hole_result.model_dump(exclude_unset=True)
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
    hole_result_id: int,
):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    session.delete(hole_result_db)
    session.commit()
    return {"ok": True}


@router.post("/validate/", response_model=RoundValidationResponse)
async def validate_round(*, round: RoundValidationRequest):
    return scoring.validate_round(round)


@router.post("/submit/", response_model=RoundSubmissionResponse)
async def submit_round(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    round: RoundSubmissionRequest,
):
    # Validate round scoring data
    round_validated = scoring.validate_round(round)
    if not round_validated.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit round with invalid scoring",
        )

    # Get golfer from database
    golfer_db = session.get(Golfer, round.golfer_id)
    if golfer_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Golfer (id={round.golfer_id}) not found",
        )

    # Get holes from database
    holes_db = session.exec(select(Hole).where(Hole.tee_id == round.tee_id)).all()
    if len(holes_db) != len(round.holes):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expected {len(round.holes)} holes, found {len(holes_db)} in database for tee (id={round.tee_id})",
        )
    holes_db = sorted(holes_db, key=lambda h: h.number)

    # Add round to database
    round_db = Round(
        tee_id=round.tee_id,
        type=round.round_type,
        scoring_type=round.scoring_type,
        date_played=datetime(
            year=round.date_played.year,
            month=round.date_played.month,
            day=round.date_played.day,
        ),
        date_updated=datetime.today(),
    )
    session.add(round_db)
    session.commit()
    session.refresh(round_db)

    # Link round to golfer
    round_golfer_link_db = RoundGolferLink(
        round_id=round_db.id,
        golfer_id=golfer_db.id,
        playing_handicap=round.course_handicap,
    )
    session.add(round_golfer_link_db)
    session.commit()
    session.refresh(round_golfer_link_db)

    # Add hole results to database
    hole_results_db: list[HoleResult] = []
    for hole_validated in round_validated.holes:
        hole_db = next(
            filter(lambda h: h.number == hole_validated.number, holes_db), None
        )
        if hole_db is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Hole #{hole_validated.number} for tee (id={round.tee_id}) not found",
            )

        hole_result_db = HoleResult(
            round_id=round_db.id,
            hole_id=hole_db.id,
            handicap_strokes=hole_validated.handicap_strokes,
            gross_score=hole_validated.gross_score,
            adjusted_gross_score=hole_validated.adjusted_gross_score,
            net_score=hole_validated.net_score,
        )
        session.add(hole_result_db)
        session.commit()
        session.refresh(hole_result_db)

        hole_results_db.append(hole_result_db)

    # Construct response from database objects
    holes_response: list[HoleResultSubmissionResponse] = []
    for hole_result_db in hole_results_db:
        hole_validated = next(
            filter(
                lambda h: h.number == hole_result_db.hole.number, round_validated.holes
            ),
            None,
        )
        if hole_validated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Validated results for hole #{hole_result_db.hole.number} not found",
            )

        holes_response.append(
            HoleResultSubmissionResponse(
                hole_result_id=hole_result_db.id,
                hole_id=hole_result_db.hole_id,
                number=hole_result_db.hole.number,
                par=hole_result_db.hole.par,
                stroke_index=hole_result_db.hole.stroke_index,
                gross_score=hole_result_db.gross_score,
                handicap_strokes=hole_result_db.handicap_strokes,
                adjusted_gross_score=hole_result_db.adjusted_gross_score,
                net_score=hole_result_db.net_score,
                max_gross_score=hole_validated.max_gross_score,
                is_valid=hole_validated.is_valid,
            )
        )

    return RoundSubmissionResponse(
        round_id=round_db.id,
        golfer_id=round_db.id,
        tee_id=round_db.tee_id,
        round_type=round_db.type,
        scoring_type=round_db.scoring_type,
        date_played=round_db.date_played,
        course_handicap=round_golfer_link_db.playing_handicap,
        holes=holes_response,
        is_valid=round_validated.is_valid,
    )
