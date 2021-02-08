r"""
Test script for USGA handicap functions

Authors
-------
Andris Jaunzemis

"""

from usga_handicap import round_toward_zero, compute_course_handicap, compute_handicap_strokes, compute_maximum_score, compute_adjusted_gross_score

def test_round_toward_zero():
    a = 8.49
    print(round_toward_zero(a, 1))
    a = 8.5
    print(round_toward_zero(a, 1))
    a = 8.51
    print(round_toward_zero(a, 1))
    a = -0.49
    print(round_toward_zero(a, 1))
    a = -0.5
    print(round_toward_zero(a, 1))
    a = -0.51
    print(round_toward_zero(a, 1))
    
def test_compute_handicap_strokes():
    handicap = 7
    index = 20
    print(compute_handicap_strokes(handicap, index))

def test_compute_maximum_score():
    par = 4
    handicap = 7
    index = 16
    print(compute_maximum_score(par, handicap, index))

def test_compute_adjusted_gross_score():
    par = 4
    handicap = 7
    score = 8
    index = 16
    print(compute_adjusted_gross_score(par, handicap, score, index=index))

def test_compute_course_handicap():
    course_par = 72
    course_rating = 73.1
    course_slope_rating = 132
    handicap_index = 12
    course_handicap = compute_course_handicap(course_par, course_rating, course_slope_rating, handicap_index)
    print(course_handicap)
    print(round_toward_zero(course_handicap))

if __name__ == '__main__':
    # test_round_toward_zero()
    # test_compute_handicap_strokes()
    # test_compute_maximum_score()
    test_compute_adjusted_gross_score()
    # test_compute_course_handicap()
