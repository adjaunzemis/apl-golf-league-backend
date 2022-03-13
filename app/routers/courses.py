from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from ..dependencies import get_current_active_user, get_session
from ..models.course import Course, CourseCreate, CourseUpdate, CourseRead, CourseReadWithTracks
from ..models.track import Track, TrackRead, TrackReadWithTees
from ..models.tee import Tee, TeeRead, TeeReadWithHoles
from ..models.hole import Hole, HoleRead
from ..models.user import User

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.get("/", response_model=List[CourseReadWithTracks])
async def read_courses(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    # TODO: Refactor querying to use joins and reduce number of queries
    return session.exec(select(Course).offset(offset).limit(limit)).all()

@router.post("/", response_model=CourseRead)
async def create_course(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), course: CourseCreate):
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
async def update_course(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), course_id: int, course: CourseUpdate):
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
async def delete_course(*, session: Session = Depends(get_session), current_user: User = Depends(get_current_active_user), course_id: int):
    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course_db)
    session.commit()
    # TODO: Delete linked resources (tracks, tees, holes, etc.)
    return {"ok": True}

@router.get("/tracks/", response_model=List[TrackRead])
async def read_tracks(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Track).offset(offset).limit(limit)).all()

@router.get("/tracks/{track_id}", response_model=TrackReadWithTees)
async def read_track(*, session: Session = Depends(get_session), track_id: int):
    track_db = session.get(Track, track_id)
    if not track_db:
        raise HTTPException(status_code=404, detail="Track not found")
    return track_db

@router.get("/tees/", response_model=List[TeeRead])
async def read_tees(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Tee).offset(offset).limit(limit)).all()

@router.get("/tees/{tee_id}", response_model=TeeReadWithHoles)
async def read_tee(*, session: Session = Depends(get_session), tee_id: int):
    tee_db = session.get(Tee, tee_id)
    if not tee_db:
        raise HTTPException(status_code=404, detail="Tee not found")
    return tee_db

@router.get("/holes/", response_model=List[HoleRead])
async def read_holes(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)):
    return session.exec(select(Hole).offset(offset).limit(limit)).all()

@router.get("/holes/{hole_id}", response_model=HoleRead)
async def read_hole(*, session: Session = Depends(get_session), hole_id: int):
    hole_db = session.get(Hole, hole_id)
    if not hole_db:
        raise HTTPException(status_code=404, detail="Hole not found")
    return hole_db
