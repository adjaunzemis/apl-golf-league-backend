import pytest
from sqlmodel import Session

from app.database import substitutes as db_substitutes
from app.models.substitutes import Substitute, SubstituteCreate


@pytest.fixture()
def session_with_substitutes(session: Session):
    session.add(Substitute(flight_id=1, golfer_id=1, division_id=1))
    session.add(Substitute(flight_id=1, golfer_id=2, division_id=1))
    session.add(Substitute(flight_id=2, golfer_id=3, division_id=1))
    session.commit()
    yield session


def test_get_substitute(session_with_substitutes):
    substitute_db = db_substitutes.get_substitute(
        session_with_substitutes, flight_id=1, golfer_id=1
    )
    assert substitute_db is not None
    assert substitute_db.flight_id == 1
    assert substitute_db.golfer_id == 1


def test_get_substitute_not_found(session_with_substitutes):
    substitute_db = db_substitutes.get_substitute(
        session_with_substitutes, flight_id=1, golfer_id=5
    )
    assert substitute_db is None


def test_get_substitutes(session_with_substitutes):
    result = db_substitutes.get_substitutes(session_with_substitutes)
    assert len(result) == 3


@pytest.mark.parametrize("flight_id, num_substitutes", [(1, 2), (2, 1), (3, 0)])
def test_get_substitutes_for_flight(
    session_with_substitutes, flight_id, num_substitutes
):
    results = db_substitutes.get_substitutes(
        session_with_substitutes, flight_id=flight_id
    )
    assert len(results) == num_substitutes
    assert len(set([sub.golfer_id for sub in results])) == num_substitutes
    for sub in results:
        assert sub.flight_id == flight_id


def test_create_substitute(session_with_substitutes):
    new_substitute = SubstituteCreate(flight_id=1, golfer_id=3, division_id=1)
    substitute_db = db_substitutes.create_substitute(
        session_with_substitutes, new_substitute
    )
    assert substitute_db.flight_id == new_substitute.flight_id
    assert substitute_db.golfer_id == new_substitute.golfer_id


def test_create_substitute_conflict(session_with_substitutes):
    new_substitute = SubstituteCreate(flight_id=1, golfer_id=1, division_id=1)
    substitute_db = db_substitutes.create_substitute(
        session_with_substitutes, new_substitute
    )
    assert substitute_db is None


def test_delete_substitute(session_with_substitutes):
    substitute_db = db_substitutes.delete_substitute(
        session_with_substitutes, flight_id=1, golfer_id=1
    )
    assert substitute_db.flight_id == 1
    assert substitute_db.golfer_id == 1
    assert (
        db_substitutes.get_substitute(
            session_with_substitutes, flight_id=1, golfer_id=1
        )
        is None
    )


def test_delete_substitute_not_found(session_with_substitutes):
    substitute = db_substitutes.delete_substitute(
        session_with_substitutes, flight_id=1, golfer_id=5
    )
    assert substitute is None
