import pytest
from sqlmodel import Session

from app.database import golfers as db_golfers
from app.models.golfer import Golfer, GolferAffiliation


@pytest.mark.parametrize(
    "input_name, expected",
    [
        ("  John  Doe  ", "john doe"),
        ("Jane Smith", "jane smith"),
        ("BOB", "bob"),
        ("  Multiple   Spaces  ", "multiple spaces"),
    ],
)
def test_normalize_name(input_name: str, expected: str):
    assert db_golfers.normalize_name(input_name) == expected


@pytest.mark.parametrize(
    "search_name, expected_count",
    [
        ("john doe", 1),
        ("  JOHN  DOE  ", 1),
        ("nonexistent", 0),
        ("jane smith", 1),
    ],
)
def test_find_exact_matches(session: Session, search_name: str, expected_count: int):
    golfer1 = Golfer(name="John Doe", affiliation=GolferAffiliation.APL_EMPLOYEE)
    golfer2 = Golfer(name="Jane Smith", affiliation=GolferAffiliation.APL_EMPLOYEE)
    session.add(golfer1)
    session.add(golfer2)
    session.commit()

    # Normalize search_name because find_exact_matches expects normalized input
    normalized_search = db_golfers.normalize_name(search_name)
    matches = db_golfers.find_exact_matches(session, normalized_search)
    assert len(matches) == expected_count
    if expected_count > 0:
        assert db_golfers.normalize_name(matches[0].name) == normalized_search


@pytest.mark.parametrize(
    "name_a, name_b, expected_score",
    [
        ("john doe", "doe john", 1.0),
        ("john doe", "john doe", 1.0),
        ("john doe", "jane doe", 0.75),  # RapidFuzz score for this pair
    ],
)
def test_score_name(name_a: str, name_b: str, expected_score: float):
    # We use >= or close comparison if needed, but for these exact ones:
    assert db_golfers.score_name(name_a, name_b) == pytest.approx(
        expected_score, abs=0.01
    )


@pytest.mark.parametrize(
    "query_name, threshold, expected_matches_count",
    [
        ("Jon Doe", 0.8, 1),
        ("Jane Smith", 0.8, 0),
    ],
)
def test_find_fuzzy_matches(
    session: Session, query_name: str, threshold: float, expected_matches_count: int
):
    golfer1 = Golfer(name="John Doe", affiliation=GolferAffiliation.APL_EMPLOYEE)
    session.add(golfer1)
    session.commit()

    candidates = [golfer1]
    matches = db_golfers.find_fuzzy_matches(query_name, candidates, threshold=threshold)
    assert len(matches) == expected_matches_count
    if expected_matches_count > 0:
        assert matches[0].name == "John Doe"


@pytest.mark.parametrize(
    "name_to_check, expected_unique, expected_exact_count, expected_fuzzy_count",
    [
        ("John Doe", False, 1, 0),  # Exact match
        ("Jon Doe", False, 0, 1),  # Fuzzy match (high score > 0.85)
        ("Jane Doe", True, 0, 1),  # Fuzzy match (low score < 0.85)
        ("Jane Smith", True, 0, 0),  # Unique
    ],
)
def test_check_golfer_name_uniqueness(
    session: Session,
    name_to_check: str,
    expected_unique: bool,
    expected_exact_count: int,
    expected_fuzzy_count: int,
):
    golfer1 = Golfer(name="John Doe", affiliation=GolferAffiliation.APL_EMPLOYEE)
    session.add(golfer1)
    session.commit()

    result = db_golfers.check_golfer_name_uniqueness(session, name_to_check)
    assert result.is_unique == expected_unique
    assert len(result.exact_matches) == expected_exact_count
    assert len(result.possible_matches) == expected_fuzzy_count
