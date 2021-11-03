r"""
Test script for USGA handicap functions

Authors
-------
Andris Jaunzemis

"""

import pytest

from usga_handicap import *

@pytest.mark.parametrize(
    "par, stroke_index, handicap_index, max_score", [
        (4, 7, 62, 9),
        (4, 7, 52, 9),
        (4, 7, 42, 8),
        (4, 7, 32, 8),
        (4, 7, 22, 7),
        (4, 7, 12, 7),
        (4, 7, 2, 6)
    ])
def test_compute_maximum_score(par, stroke_index, handicap_index, max_score):
    assert compute_maximum_score(par, stroke_index, handicap_index) == max_score

@pytest.mark.parametrize(
    "stroke_index, handicap_index, handicap_strokes", [
        (5, 63, 4),
        (5, 53, 3),
        (5, 43, 3),
        (5, 33, 2),
        (5, 23, 2),
        (5, 13, 1),
        (5, 3, 0)
    ])
def test_compute_handicap_strokes(stroke_index, handicap_index, handicap_strokes):
    assert compute_handicap_strokes(stroke_index, handicap_index) == handicap_strokes

@pytest.mark.parametrize(
    "par, stroke_index, score, handicap_index, adjusted_score", [
        (4, 7, 8, 16, 7)
    ])
def test_compute_adjusted_gross_score(par, stroke_index, score, handicap_index, adjusted_score):
    assert compute_adjusted_gross_score(par, stroke_index, score, handicap_index=handicap_index) == adjusted_score
    
@pytest.mark.parametrize(
    "course_par, course_rating, course_slope_rating, handicap_index, course_handicap", [
        (72, 73.1, 132, 12, 15.12)
    ])
def test_compute_course_handicap(course_par, course_rating, course_slope_rating, handicap_index, course_handicap):
    assert pytest.approx(compute_course_handicap(course_par, course_rating, course_slope_rating, handicap_index), abs=1e-2) == course_handicap
