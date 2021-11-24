import pytest

from .world_handicap_system import WorldHandicapSystem

@pytest.mark.parametrize(
    "par, stroke_index, course_handicap, max_score", [
        (4, 7, 60, 9),
        (4, 7, 52, 9),
        (4, 7, 42, 8),
        (4, 7, 32, 8),
        (4, 7, 22, 7),
        (4, 7, 12, 7),
        (4, 7, 2, 6)
    ])
def test_compute_hole_maximum_score(par, stroke_index, course_handicap, max_score):
    whs = WorldHandicapSystem()
    assert whs.compute_hole_maximum_score(par, stroke_index, course_handicap) == max_score

@pytest.mark.parametrize(
    "stroke_index, handicap_index, handicap_strokes", [
        (5, 59, 4),
        (5, 53, 3),
        (5, 43, 3),
        (5, 41, 3),
        (5, 33, 2),
        (5, 23, 2),
        (5, 20, 1),
        (5, 13, 1),
        (5, 5, 1),
        (5, 3, 0),
        (5, 0, 0),
        (5, -2, 0),
        (5, -5, -1),
        (5, -9, -1),
        (5, -18, -1),
        (5, -23, -2),
        (5, -25, -2),
    ])
def test_compute_hole_handicap_strokes(stroke_index, handicap_index, handicap_strokes):
    whs = WorldHandicapSystem()
    assert whs.compute_hole_handicap_strokes(stroke_index, handicap_index) == handicap_strokes

@pytest.mark.parametrize(
    "par, stroke_index, score, handicap_index, adjusted_score", [
        (4, 7, 8, 16, 7)
    ])
def test_compute_hole_adjusted_gross_score(par, stroke_index, score, handicap_index, adjusted_score):
    whs = WorldHandicapSystem()
    assert whs.compute_hole_adjusted_gross_score(par, stroke_index, score, course_handicap=handicap_index) == adjusted_score
    
@pytest.mark.parametrize(
    "course_par, course_rating, course_slope_rating, handicap_index, course_handicap", [
        (72, 73.1, 132, 12, 15.12)
    ])
def test_compute_course_handicap(course_par, course_rating, course_slope_rating, handicap_index, course_handicap):
    whs = WorldHandicapSystem()
    assert pytest.approx(whs.compute_course_handicap(course_par, course_rating, course_slope_rating, handicap_index), abs=1e-2) == course_handicap
