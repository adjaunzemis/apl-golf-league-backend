import pytest

from .apl_legacy_handicap_system import APLLegacyHandicapSystem

@pytest.mark.parametrize(
    "par, stroke_index, course_handicap, max_score", [
        (4, 7, 30, 10),
        (4, 7, 25, 10),
        (4, 7, 20, 10),
        (4, 7, 19, 9),
        (4, 7, 15, 9),
        (4, 7, 14, 8),
        (4, 7, 10, 8),
        (4, 7, 9, 7),
        (4, 7, 5, 7),
        (4, 7, 4, 6),
        (4, 7, 0, 6),
        (4, 7, -1, 6),
        (4, 1, 4, 6),
        (4, 9, 4, 6),
        (5, 9, 4, 7),
        (3, 9, 4, 5)
    ])
def test_compute_hole_maximum_score(par, stroke_index, course_handicap, max_score):
    alhs = APLLegacyHandicapSystem()
    assert alhs.compute_hole_maximum_score(par, stroke_index, course_handicap) == max_score

@pytest.mark.parametrize(
    "stroke_index, course_handicap, handicap_strokes", [
        (5, 30, 4),
        (5, 27, 3),
        (5, 21, 3),
        (5, 18, 2),
        (5, 12, 2),
        (5, 9, 1),
        (5, 3, 1),
        (5, 2, 0),
        (5, 0, 0),
        (5, -2, 0),
        (5, -3, -1),
        (5, -9, -1),
        (5, -12, -2)
    ])
def test_compute_hole_handicap_strokes(stroke_index, course_handicap, handicap_strokes):
    alhs = APLLegacyHandicapSystem()
    assert alhs.compute_hole_handicap_strokes(stroke_index, course_handicap) == handicap_strokes

@pytest.mark.parametrize(
    "par, stroke_index, score, course_handicap, adjusted_score", [
        (4, 7, 8, 16, 8),
        (4, 7, 11, 20, 10),
        (4, 7, 11, 15, 9),
        (4, 7, 11, 10, 8),
        (4, 7, 11, 5, 7),
        (4, 7, 11, 4, 6),
        (5, 7, 11, 15, 9),
        (5, 7, 11, 2, 7),
        (4, 1, 11, 1, 6),
        (4, 9, 11, 1, 6)
    ])
def test_compute_hole_adjusted_gross_score(par, stroke_index, score, course_handicap, adjusted_score):
    alhs = APLLegacyHandicapSystem()
    assert alhs.compute_hole_adjusted_gross_score(par, stroke_index, score, course_handicap=course_handicap) == adjusted_score
    
@pytest.mark.parametrize(
    "course_par, course_rating, course_slope, handicap_index, course_handicap", [
        (72, 73.1, 132, 12, 15.12),
        (36, 36.7, 123, 4.2, 5), # TODO: Move to playing handicap test
        (36, 34.7, 134, 13.1, 15) # TODO: Move to playing handicap test
    ])
def test_compute_course_handicap(course_par, course_rating, course_slope, handicap_index, course_handicap):
    alhs = APLLegacyHandicapSystem()
    assert pytest.approx(alhs.compute_course_handicap(course_par, course_rating, course_slope, handicap_index), abs=1e-2) == course_handicap

@pytest.mark.parametrize(
    "course_rating, course_slope, adj_gross_score, pcc, score_diff", [
        (70.9, 121, 83, 0, 11.3),
        (70.9, 121, 82, 0, 10.4),
        (68.7, 115, 92, 0, 22.9),
        (68.7, 115, 92, -0.5, 23.4),
        (68.7, 115, 92, 1.5, 21.4),
        (71.1, 124, 73, 0, 1.7),
        (71.1, 122, 71, 0, -0.1),
        (71.1, 122, 68, 0, -2.9),
        (70.6, 133, 68, 0, -2.2)
    ])
def test_compute_score_differential(course_rating, course_slope, adj_gross_score, pcc, score_diff):
    alhs = APLLegacyHandicapSystem()
    assert alhs.compute_score_differential(course_rating, course_slope, adj_gross_score, pcc) == score_diff

@pytest.mark.parametrize(
    "records, handicap_index", [
        ([4.5, 5.6, 3.4, 8.7, 6.8, 10.2, 4.3, 8.8, 6.2, 4.8], 4.3),
        ([13.4, 16.7, 21.2, 13.9], 13.1)
    ])
def test_compoute_handicap_index(records, handicap_index):
    alhs = APLLegacyHandicapSystem()
    assert alhs.compute_handicap_index(records) == handicap_index

def test_maximum_handicap_index():
    alhs = APLLegacyHandicapSystem()
    assert alhs.maximum_handicap_index == 30.0
