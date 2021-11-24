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
    "stroke_index, course_handicap, handicap_strokes", [
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
def test_compute_hole_handicap_strokes(stroke_index, course_handicap, handicap_strokes):
    whs = WorldHandicapSystem()
    assert whs.compute_hole_handicap_strokes(stroke_index, course_handicap) == handicap_strokes

@pytest.mark.parametrize(
    "par, stroke_index, score, course_handicap, adjusted_score", [
        (4, 7, 8, 16, 7)
    ])
def test_compute_hole_adjusted_gross_score(par, stroke_index, score, course_handicap, adjusted_score):
    whs = WorldHandicapSystem()
    assert whs.compute_hole_adjusted_gross_score(par, stroke_index, score, course_handicap=course_handicap) == adjusted_score
    
@pytest.mark.parametrize(
    "course_par, course_rating, course_slope_rating, handicap_index, course_handicap", [
        (72, 73.1, 132, 12, 15.12)
    ])
def test_compute_course_handicap(course_par, course_rating, course_slope_rating, handicap_index, course_handicap):
    whs = WorldHandicapSystem()
    assert pytest.approx(whs.compute_course_handicap(course_par, course_rating, course_slope_rating, handicap_index), abs=1e-2) == course_handicap

@pytest.mark.parametrize(
    "records, handicap_index", [
        ([15.3,], 13.3),
        ([15.3, 15.2], 13.2),
        ([15.3, 15.2, 16.6], 13.2),
        ([15.3, 15.2, 16.6, 16.0], 14.2),
        ([15.3, 15.2, 16.6, 16.0, 15.7], 15.2),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5], 14.2),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1], 15.2),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9], 15.2),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8], 15.1),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4], 15.1),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7], 15.1),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5], 14.7),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5, 15.7], 14.7),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5, 15.7, 16.9], 14.7),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5, 15.7, 16.9, 16.0], 14.8),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5, 15.7, 16.9, 16.0, 13.2], 14.4),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5, 15.7, 16.9, 16.0, 13.2, 16.1], 14.6),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5, 15.7, 16.9, 16.0, 13.2, 16.1, 15.9], 14.6),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5, 15.7, 16.9, 16.0, 13.2, 16.1, 15.9, 12.5], 14.3),
        ([15.3, 15.2, 16.6, 16.0, 15.7, 15.5, 16.1, 15.9, 14.8, 15.4, 15.7, 13.5, 15.7, 16.9, 16.0, 13.2, 16.1, 15.9, 12.5, 15.8], 14.4),
        ([40.7, 42.4, 36.1], 34.1),
        ([40.7, 42.4, 36.1, 45.9, 43.6, 45.0], 37.4),
    ])
def test_compoute_handicap_index(records, handicap_index):
    whs = WorldHandicapSystem()
    assert whs.compute_handicap_index(records) == handicap_index

def test_maximum_handicap_index():
    whs = WorldHandicapSystem()
    assert whs.maximum_handicap_index == 54.0
