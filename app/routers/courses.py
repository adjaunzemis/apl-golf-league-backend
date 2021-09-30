from typing import List
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select
from sqlmodel.main import Relationship

from ..dependencies import get_session
from ..models.course import Course, CourseRead, CourseCreate, CourseUpdate

router = APIRouter(
    prefix="/courses",
    tags=["courses"]
)

@router.get("/", response_model=List[CourseRead])
async def read_courses(*, session: Session = Depends(get_session), offset: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100)) -> List[CourseRead]:
    return session.exec(select(Course).offset(offset).limit(limit)).all()
    
@router.post("/", response_model=CourseRead)
async def create_course(*, session: Session = Depends(get_session), course: CourseCreate) -> CourseRead:
    course_db = Course.from_orm(course)
    session.add(course_db)
    session.commit()
    session.refresh(course_db)
    return course_db

@router.get("/{course_id}", response_model=CourseRead) # TODO: CourseReadWithTracks
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
