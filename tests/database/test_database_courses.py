import pytest
from sqlmodel import Session

from app.database import courses as db_course
from app.models.course import Course
from app.models.hole import Hole
from app.models.tee import Tee, TeeGender
from app.models.track import Track


@pytest.fixture()
def course_data_woodholme() -> tuple[Course, list[Track], list[Tee], list[Hole]]:
    course = Course(
        id=1,
        name="Woodholme Country Club",
        year=2024,
        address="Pikesville, MD",
    )

    track_front = Track(
        id=1,
        course_id=course.id,
        name="Front",
    )

    tee_front_blue = Tee(
        id=1,
        track_id=track_front.id,
        name="Blue",
        gender=TeeGender.MENS,
        rating=34.8,
        slope=133,
    )

    holes_front_blue = [
        Hole(
            id=1, tee_id=tee_front_blue.id, number=1, par=4, yardage=325, stroke_index=9
        ),
        Hole(
            id=2, tee_id=tee_front_blue.id, number=2, par=5, yardage=529, stroke_index=4
        ),
        Hole(
            id=3, tee_id=tee_front_blue.id, number=3, par=3, yardage=164, stroke_index=6
        ),
        Hole(
            id=4, tee_id=tee_front_blue.id, number=4, par=4, yardage=401, stroke_index=1
        ),
        Hole(
            id=5, tee_id=tee_front_blue.id, number=5, par=3, yardage=186, stroke_index=7
        ),
        Hole(
            id=6, tee_id=tee_front_blue.id, number=6, par=4, yardage=404, stroke_index=3
        ),
        Hole(
            id=7, tee_id=tee_front_blue.id, number=7, par=4, yardage=337, stroke_index=5
        ),
        Hole(
            id=8, tee_id=tee_front_blue.id, number=8, par=4, yardage=306, stroke_index=8
        ),
        Hole(
            id=9, tee_id=tee_front_blue.id, number=9, par=4, yardage=366, stroke_index=2
        ),
    ]

    track_back = Track(
        id=2,
        course_id=course.id,
        name="Back",
    )

    tee_back_blue = Tee(
        id=2,
        track_id=track_back.id,
        name="Blue",
        gender=TeeGender.MENS,
        rating=36.8,
        slope=135,
    )

    holes_back_blue = [
        Hole(
            id=10,
            tee_id=tee_back_blue.id,
            number=10,
            par=4,
            yardage=359,
            stroke_index=8,
        ),
        Hole(
            id=11,
            tee_id=tee_back_blue.id,
            number=11,
            par=5,
            yardage=497,
            stroke_index=3,
        ),
        Hole(
            id=12,
            tee_id=tee_back_blue.id,
            number=12,
            par=5,
            yardage=493,
            stroke_index=6,
        ),
        Hole(
            id=13,
            tee_id=tee_back_blue.id,
            number=13,
            par=3,
            yardage=155,
            stroke_index=9,
        ),
        Hole(
            id=14,
            tee_id=tee_back_blue.id,
            number=14,
            par=4,
            yardage=364,
            stroke_index=2,
        ),
        Hole(
            id=15,
            tee_id=tee_back_blue.id,
            number=15,
            par=4,
            yardage=426,
            stroke_index=1,
        ),
        Hole(
            id=16,
            tee_id=tee_back_blue.id,
            number=16,
            par=5,
            yardage=487,
            stroke_index=5,
        ),
        Hole(
            id=17,
            tee_id=tee_back_blue.id,
            number=17,
            par=3,
            yardage=203,
            stroke_index=4,
        ),
        Hole(
            id=18,
            tee_id=tee_back_blue.id,
            number=18,
            par=5,
            yardage=459,
            stroke_index=7,
        ),
    ]

    return (
        course,
        [track_front, track_back],
        [tee_front_blue, tee_back_blue],
        holes_front_blue + holes_back_blue,
    )


@pytest.fixture()
def session_woodholme(session: Session, course_data_woodholme):
    session.add(course_data_woodholme[0])
    for track in course_data_woodholme[1]:
        session.add(track)
    for tee in course_data_woodholme[2]:
        session.add(tee)
    for hole in course_data_woodholme[3]:
        session.add(hole)
    yield session


def test_get_course_data_by_tee_id(session_woodholme: Session):
    # Get course data from database
    course_data_db = db_course.get_course_data_by_tee_id(
        session=session_woodholme, tee_id=2
    )

    # Assert expected course data
    assert course_data_db is not None

    course_db = course_data_db[0]
    assert course_db.name == "Woodholme Country Club"
    assert course_db.year == 2024

    track_db = course_data_db[1]
    assert track_db.name == "Back"

    tee_db = course_data_db[2]
    assert tee_db.name == "Blue"

    holes_db = course_data_db[3]
    assert len(holes_db) == 9
    assert holes_db[0].number == 10
    assert holes_db[0].par == 4
    assert holes_db[-1].number == 18
    assert holes_db[-1].par == 5


def test_get_course_data_by_tee_id_invalid_tee_id(session: Session):
    with pytest.raises(ValueError):
        db_course.get_course_data_by_tee_id(session=session, tee_id=1)
