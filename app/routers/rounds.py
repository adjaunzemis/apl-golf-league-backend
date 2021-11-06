from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.round import Round, RoundCreate, RoundUpdate, RoundRead, RoundReadWithData, RoundData, RoundDataWithCount
from ..models.hole_result import HoleResult, HoleResultCreate, HoleResultUpdate, HoleResultRead, HoleResultReadWithHole, HoleResultData
from ..models.course import Course
from ..models.track import Track
from ..models.tee import Tee
from ..models.hole import Hole
from ..models.golfer import Golfer
from ..utilities.usga_handicap import compute_handicap_strokes, compute_adjusted_gross_score

router = APIRouter(
    prefix="/rounds",
    tags=["Rounds"]
)
    
@router.get("/", response_model=RoundDataWithCount)
async def read_rounds(*, session: Session = Depends(get_session), golfer_id: int = Query(default=None, ge=0), offset: int = Query(default=0, ge=0), limit: int = Query(default=25, ge=0, le=100)):
    # Process query parameters to further limit round results returned from database
    if golfer_id: # limit to specific golfer
        num_rounds = len(session.exec(select(Round.id).where(Round.golfer_id == golfer_id)).all())
        round_query_data = session.exec(select(Round, Golfer, Course, Tee).join(Golfer).join(Tee).join(Track).join(Course).where(Round.golfer_id == golfer_id).offset(offset).limit(limit).order_by(Round.date_played))
    else: # no extra limitations
        num_rounds = len(session.exec(select(Round.id)).all())
        round_query_data = session.exec(select(Round, Golfer, Course, Tee).join(Golfer).join(Tee).join(Track).join(Course).offset(offset).limit(limit).order_by(Round.date_played))

    # Reformat round data
    if num_rounds == 0:
        return RoundDataWithCount(num_rounds=0, rounds=[])

    round_data = [RoundData(
        round_id=round.id,
        date_played=round.date_played,
        golfer_name=golfer.name,
        golfer_handicap_index=round.handicap_index,
        golfer_playing_handicap=round.playing_handicap,
        course_name=course.name,
        tee_name=tee.name,
        tee_rating=tee.rating,
        tee_slope=tee.slope
    ) for round, golfer, course, tee in round_query_data]

    # Query hole data for selected rounds
    hole_query_data = session.exec(select(HoleResult, Hole).join(Hole).where(HoleResult.round_id.in_([r.round_id for r in round_data])))
    hole_result_data = [HoleResultData(
        hole_result_id=hole_result.id,
        round_id=hole_result.round_id,
        number=hole.number,
        par=hole.par,
        yardage=hole.yardage,
        stroke_index=hole.stroke_index,
        gross_score=hole_result.strokes
    ) for hole_result, hole in hole_query_data]

    # Add hole data to round data
    # TODO: Compute handicap strokes and non-gross scores on entry to database
    for r in round_data:
        r.holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in r.holes])
        r.gross_score = sum([h.gross_score for h in r.holes])
        for h in r.holes:
            h.handicap_strokes = compute_handicap_strokes(h.stroke_index, r.golfer_playing_handicap)
            h.adjusted_gross_score = compute_adjusted_gross_score(h.par, h.stroke_index, h.gross_score, handicap_index=r.golfer_playing_handicap)
            h.net_score = h.gross_score - h.handicap_strokes
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in r.holes])
        r.net_score = sum([h.net_score for h in r.holes])

    # Return count of relevant rounds from database and round data list
    return RoundDataWithCount(num_rounds=num_rounds, rounds=round_data)

@router.post("/", response_model=RoundRead)
async def create_round(*, session: Session = Depends(get_session), round: RoundCreate):
    round_db = Round.from_orm(round)
    session.add(round_db)
    session.commit()
    session.refresh(round_db)
    return round_db

@router.get("/{round_id}", response_model=RoundReadWithData)
async def read_round(*, session: Session = Depends(get_session), round_id: int):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    return round_db

@router.patch("/{round_id}", response_model=RoundRead)
async def update_round(*, session: Session = Depends(get_session), round_id: int, round: RoundUpdate):
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
async def delete_round(*, session: Session = Depends(get_session), round_id: int):
    round_db = session.get(Round, round_id)
    if not round_db:
        raise HTTPException(status_code=404, detail="Round not found")
    session.delete(round_db)
    session.commit()
    return {"ok": True}

@router.get("/hole_results/", response_model=List[HoleResultRead])
async def read_hole_results(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(HoleResult).offset(offset).limit(limit)).all()

@router.post("/hole_results/", response_model=HoleResultRead)
async def create_hole_result(*, session: Session = Depends(get_session), hole_result: HoleResultCreate):
    hole_result_db = HoleResult.from_orm(hole_result)
    session.add(hole_result_db)
    session.commit()
    session.refresh(hole_result_db)
    return hole_result_db

@router.get("/hole_results/{hole_result_id}", response_model=HoleResultReadWithHole)
async def read_hole_result(*, session: Session = Depends(get_session), hole_result_id: int):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    return hole_result_db

@router.patch("/hole_results/{hole_result_id}", response_model=HoleResultRead)
async def update_hole_result(*, session: Session = Depends(get_session), hole_result_id: int, hole_result: HoleResultUpdate):
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
async def delete_hole_result(*, session: Session = Depends(get_session), hole_result_id: int):
    hole_result_db = session.get(HoleResult, hole_result_id)
    if not hole_result_db:
        raise HTTPException(status_code=404, detail="Hole result not found")
    session.delete(hole_result_db)
    session.commit()
    return {"ok": True}
