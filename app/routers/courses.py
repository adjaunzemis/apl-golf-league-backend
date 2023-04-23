from typing import List, Optional
from http import HTTPStatus
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select, SQLModel

from ..dependencies import get_current_active_user, get_sql_db_session
from ..models.course import (
    Course,
    CourseUpdate,
    CourseRead,
    CourseReadWithTracks,
)
from ..models.track import Track, TrackRead, TrackReadWithTees
from ..models.tee import Tee, TeeGender, TeeRead, TeeReadWithHoles
from ..models.hole import Hole, HoleRead
from ..models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])


class HoleData(SQLModel):
    id: Optional[int] = None
    number: int
    par: int
    yardage: Optional[int] = None
    stroke_index: int


class TeeData(SQLModel):
    id: Optional[int] = None
    name: str
    gender: TeeGender
    rating: float
    slope: int
    holes: List[HoleData] = []


class TrackData(SQLModel):
    id: Optional[int] = None
    name: str
    tees: List[TeeData] = []


class CourseData(SQLModel):
    id: Optional[int] = None
    name: str
    year: int
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    tracks: List[TrackData] = []


@router.get("/", response_model=List[CourseRead])
async def read_courses(
    *,
    session: Session = Depends(get_sql_db_session),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100),
):
    # TODO: Refactor querying to use joins and reduce number of queries
    return session.exec(select(Course).offset(offset).limit(limit)).all()


@router.get("/{course_id}", response_model=CourseReadWithTracks)
async def read_course(
    *, session: Session = Depends(get_sql_db_session), course_id: int
):
    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")
    return course_db


@router.post("/", response_model=CourseRead)
async def create_course(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    course_data: CourseData,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to create courses",
        )

    validate_course_data(session=session, course_data=course_data)

    return upsert_course(session=session, course_data=course_data)


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    course_id: int,
    course_data: CourseData,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to update courses",
        )

    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Course not found")

    validate_course_data(
        session=session, course_data=course_data, exclude_course_id=course_id
    )

    return upsert_course(session=session, course_data=course_data)


@router.delete("/{course_id}")
async def delete_course(
    *,
    session: Session = Depends(get_sql_db_session),
    current_user: User = Depends(get_current_active_user),
    course_id: int,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="User not authorized to delete courses",
        )
    course_db = session.get(Course, course_id)
    if not course_db:
        raise HTTPException(status_code=404, detail="Course not found")
    session.delete(course_db)
    session.commit()

    # TODO: Delete linked resources (tracks, tees, holes, etc.)

    return {"ok": True}


@router.get("/tees/{tee_id}", response_model=TeeReadWithHoles)
async def read_tee(*, session: Session = Depends(get_sql_db_session), tee_id: int):
    tee_db = session.get(Tee, tee_id)
    if not tee_db:
        raise HTTPException(status_code=404, detail="Tee not found")
    return tee_db


def validate_course_data(
    *,
    session: Session,
    course_data: CourseData,
    exclude_course_id: Optional[int] = None,
) -> None:
    """Raises exception if given course data is not valid for creation/update."""
    # Check if course name and year are valid
    if exclude_course_id is None:
        course_db = session.exec(
            select(Course)
            .where(Course.name == course_data.name)
            .where(Course.year == course_data.year)
        ).one_or_none()
    else:
        course_db = session.exec(
            select(Course)
            .where(Course.name == course_data.name)
            .where(Course.year == course_data.year)
            .where(Course.id != exclude_course_id)
        ).one_or_none()
    if course_db:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Course '{course_data.name} ({course_data.year})' already exists",
        )

    # TODO: Check that existing (id != None) items exist
    # TODO: Check that children of new (id = None) items are also new (id = None)
    # TODO: Check whether rounds exist on this course already - stop update? update rounds?


def upsert_course(*, session: Session, course_data: CourseData) -> CourseRead:
    """Updates/inserts a course data record."""
    if course_data.id is None:  # create new course
        course_db = Course.from_orm(course_data)
    else:  # update existing course
        course_db = session.get(Course, course_data.id)
        if not course_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Course (id={course_data.id}) not found",
            )
        course_dict = course_data.dict(exclude_unset=True)
        for key, value in course_dict.items():
            setattr(course_db, key, value)
    session.add(course_db)
    session.commit()
    session.refresh(course_db)

    for track in course_data.tracks:
        upsert_track(session=session, track_data=track, course_id=course_db.id)

    session.refresh(course_db)
    return course_db


def upsert_track(
    *, session: Session, track_data: TrackData, course_id: int
) -> TrackRead:
    """Updates/inserts a track data record."""
    if track_data.id is None:  # create new track
        track_db = Track.from_orm(track_data)
    else:  # update existing track
        track_db = session.get(Track, track_data.id)
        if not track_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Track (id={track_data.id}) not found",
            )
        track_dict = track_data.dict(exclude_unset=True)
        for key, value in track_dict.items():
            setattr(track_db, key, value)
    setattr(track_db, "course_id", course_id)
    session.add(track_db)
    session.commit()
    session.refresh(track_db)

    for tee in track_data.tees:
        upsert_tee(session=session, tee_data=tee, track_id=track_db.id)

    session.refresh(track_db)
    return track_db


def upsert_tee(*, session: Session, tee_data: TeeData, track_id: int) -> TeeRead:
    """Updates/inserts a tee data record."""
    if tee_data.id is None:  # create new tee
        tee_db = Tee.from_orm(tee_data)
    else:  # update existing tee
        tee_db = session.get(Tee, tee_data.id)
        if not tee_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Tee (id={tee_data.id}) not found",
            )
        track_dict = tee_data.dict(exclude_unset=True)
        for key, value in track_dict.items():
            setattr(tee_db, key, value)
    setattr(tee_db, "track_id", track_id)
    session.add(tee_db)
    session.commit()
    session.refresh(tee_db)

    for hole in tee_data.holes:
        upsert_hole(session=session, hole_data=hole, tee_id=tee_db.id)

    session.refresh(tee_db)
    return tee_db


def upsert_hole(*, session: Session, hole_data: HoleData, tee_id: int) -> TeeRead:
    """Updates/inserts a hole data record."""
    if hole_data.id is None:  # create new hole
        hole_db = Hole.from_orm(hole_data)
    else:  # update existing hole
        hole_db = session.get(Hole, hole_data.id)
        if not hole_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Hole (id={hole_data.id}) not found",
            )
        track_dict = hole_data.dict(exclude_unset=True)
        for key, value in track_dict.items():
            setattr(hole_db, key, value)
    setattr(hole_db, "tee_id", tee_id)
    session.add(hole_db)
    session.commit()
    session.refresh(hole_db)
    return hole_db
