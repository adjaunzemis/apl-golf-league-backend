r"""
USGA handicap calculation

TODO: Refactor this, this is actually WHS!

Authors
-------
Andris Jaunzemis

"""

from .handicap_system import HandicapSystem

class USGAHandicapSystem(HandicapSystem):

    @staticmethod
    def compute_adjusted_gross_score(par: int, stroke_index: int, score: int, course_handicap: int = None) -> int:
        return min(score, USGAHandicapSystem.compute_maximum_score(par, stroke_index, course_handicap=course_handicap))

    @staticmethod
    def compute_maximum_score(par: int, stroke_index: int, course_handicap: int = None) -> int:
        if course_handicap is None:
            return par + 5
        handicap_strokes = USGAHandicapSystem.compute_handicap_strokes(stroke_index, course_handicap)
        if handicap_strokes > 3:
            return par + 5
        return par + 2 + handicap_strokes

    @staticmethod
    def compute_handicap_strokes(stroke_index: int, course_handicap: int) -> int:
        strokes = 0
        if stroke_index > 0:
            while course_handicap > 18:
                strokes += 1
                course_handicap -= 18
            if stroke_index <= course_handicap:
                strokes += 1
        else:
            if (18 - stroke_index) < abs(course_handicap):
                strokes -= 1
        return strokes

    @staticmethod
    def compute_course_handicap(par: int, rating: float, slope: int, handicap_index: float) -> float:
        return handicap_index * (slope / 113) + (rating - par)

    @staticmethod
    def compute_score_differential(rating: float, slope: int, score: int, playing_conditions_correction: float = 0.0):
        score_diff = (113 / slope) * (score - rating - playing_conditions_correction)
        return round(score_diff * 10, 1)
