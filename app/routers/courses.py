from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_session
from ..models.course import Course, CourseCreate, CourseUpdate, CourseRead, CourseReadWithTracks
from ..models.track import Track, TrackCreate, TrackUpdate, TrackRead, TrackReadWithTees
from ..models.tee import Tee, TeeCreate, TeeUpdate, TeeRead, TeeReadWithHoles
from ..models.hole import Hole, HoleCreate, HoleUpdate, HoleRead

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.get("/", response_model=List[CourseRead])
async def read_courses(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Course).offset(offset).limit(limit)).all()

@router.post("/", response_model=CourseRead)
async def create_course(*, session: Session = Depends(get_session), course: CourseCreate):
    course_db = Course.from_orm(course)
    session.add(course_db)
    session.commit()
    session.refresh(course_db)
    return course_db

@router.get("/{course_id}", response_model=CourseReadWithTracks)
async def read_course(*, session: Session = Depends(get_session), course_id: int):
    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")
    return course_db

@router.patch("/{course_id}", response_model=CourseRead)
async def update_course(*, session: Session = Depends(get_session), course_id: int, course: CourseUpdate):
    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")
    course_data = course.dict(exclude_unset=True)
    for key, value in course_data.items():
        setattr(course_db, key, value)
    session.add(course_db)
    session.commit()
    session.refresh(course_db)
    return course_db

@router.delete("/{course_id}")
async def delete_course(*, session: Session = Depends(get_session), course_id: int):
    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course_db)
    session.commit()
    return {"ok": True}

@router.get("/tracks/", response_model=List[TrackRead])
async def read_tracks(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Track).offset(offset).limit(limit)).all()

@router.post("/tracks/", response_model=TrackRead)
async def create_track(*, session: Session = Depends(get_session), track: TrackCreate):
    track_db = Track.from_orm(track)
    session.add(track_db)
    session.commit()
    session.refresh(track_db)
    return track_db

@router.get("/tracks/{track_id}", response_model=TrackReadWithTees)
async def read_track(*, session: Session = Depends(get_session), track_id: int):
    track_db = session.get(Track, track_id)
    if not track_db:
        raise HTTPException(status_code=404, detail="Track not found")
    return track_db

@router.patch("/tracks/{track_id}", response_model=TrackRead)
async def update_track(*, session: Session = Depends(get_session), track_id: int, track: TrackUpdate):
    track_db = session.get(Track, track_id)
    if not track_db:
        raise HTTPException(status_code=404, detail="Track not found")
    track_data = track.dict(exclude_unset=True)
    for key, value in track_data.items():
        setattr(track_db, key, value)
    session.add(track_db)
    session.commit()
    session.refresh(track_db)
    return track_db

@router.delete("/tracks/{track_id}")
async def delete_track(*, session: Session = Depends(get_session), track_id: int):
    track_db = session.get(Track, track_id)
    if not track_db:
        raise HTTPException(status_code=404, detail="Track not found")
    session.delete(track_db)
    session.commit()
    return {"ok": True}

@router.get("/tees/", response_model=List[TeeRead])
async def read_tees(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Tee).offset(offset).limit(limit)).all()

@router.post("/tees/", response_model=TeeRead)
async def create_tee(*, session: Session = Depends(get_session), tee: TeeCreate):
    tee_db = Tee.from_orm(tee)
    session.add(tee_db)
    session.commit()
    session.refresh(tee_db)
    return tee_db

@router.get("/tees/{tee_id}", response_model=TeeReadWithHoles)
async def read_tee(*, session: Session = Depends(get_session), tee_id: int):
    tee_db = session.get(Tee, tee_id)
    if not tee_db:
        raise HTTPException(status_code=404, detail="Tee not found")
    return tee_db

@router.patch("/tees/{tee_id}", response_model=TeeRead)
async def update_tee(*, session: Session = Depends(get_session), tee_id: int, tee: TeeUpdate):
    tee_db = session.get(Tee, tee_id)
    if not tee_db:
        raise HTTPException(status_code=404, detail="Tee not found")
    tee_data = tee.dict(exclude_unset=True)
    for key, value in tee_data.items():
        setattr(tee_db, key, value)
    session.add(tee_db)
    session.commit()
    session.refresh(tee_db)
    return tee_db

@router.delete("/tees/{tee_id}")
async def delete_tee(*, session: Session = Depends(get_session), tee_id: int):
    tee_db = session.get(Tee, tee_id)
    if not tee_db:
        raise HTTPException(status_code=404, detail="Tee not found")
    session.delete(tee_db)
    session.commit()
    return {"ok": True}

@router.get("/holes/", response_model=List[HoleRead])
async def read_holes(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Hole).offset(offset).limit(limit)).all()

@router.post("/holes/", response_model=HoleRead)
async def create_hole(*, session: Session = Depends(get_session), hole: HoleCreate):
    hole_db = Hole.from_orm(hole)
    session.add(hole_db)
    session.commit()
    session.refresh(hole_db)
    return hole_db

@router.get("/holes/{hole_id}", response_model=HoleRead) # TODO: HoleReadWithTee
async def read_hole(*, session: Session = Depends(get_session), hole_id: int):
    hole_db = session.get(Hole, hole_id)
    if not hole_db:
        raise HTTPException(status_code=404, detail="Hole not found")
    return hole_db

@router.patch("/holes/{hole_id}", response_model=HoleRead)
async def update_hole(*, session: Session = Depends(get_session), hole_id: int, hole: HoleUpdate):
    hole_db = session.get(Hole, hole_id)
    if not hole_db:
        raise HTTPException(status_code=404, detail="Hole not found")
    hole_data = hole.dict(exclude_unset=True)
    for key, value in hole_data.items():
        setattr(hole_db, key, value)
    session.add(hole_db)
    session.commit()
    session.refresh(hole_db)
    return hole_db

@router.delete("/holes/{hole_id}")
async def delete_hole(*, session: Session = Depends(get_session), hole_id: int):
    hole_db = session.get(Hole, hole_id)
    if not hole_db:
        raise HTTPException(status_code=404, detail="Hole not found")
    session.delete(hole_db)
    session.commit()
    return {"ok": True}
