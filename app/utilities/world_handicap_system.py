from typing import List

from .handicap_system import HandicapSystem

class WorldHandicapSystem(HandicapSystem):
    """
    World Handicap System (WHS) implementation of a golf handicap system.

    References
    ----------
    - USGA 2020 Rules of Handicapping: https://www.usga.org/handicapping/roh/2020-rules-of-handicapping.html
        - Note: USGA adopted WHS in 2020

    """

    def compute_hole_adjusted_gross_score(self, par: int, stroke_index: int, score: int, course_handicap: int = None) -> int:
        # Reference: USGA 2020 RoH 3.1
        return min(score, self.compute_hole_maximum_score(par, stroke_index, course_handicap=course_handicap))

    def compute_hole_maximum_score(self, par: int, stroke_index: int, course_handicap: int = None) -> int:
        # Reference: USGA 2020 RoH 3.1
        if course_handicap is None: # handicap not established
            return par + 5
        return min(par + 2 + self.compute_hole_handicap_strokes(stroke_index, course_handicap), par + 5)

    def compute_hole_handicap_strokes(self, stroke_index: int, course_handicap: int) -> int:
        if course_handicap < 0: # plus-handicap
            return -(int(-course_handicap / 18) + int(-course_handicap % 18 >= stroke_index))
        return int(course_handicap / 18) + int(course_handicap % 18 >= stroke_index)

    def compute_course_handicap(self, par: int, rating: float, slope: int, handicap_index: float) -> float:
        # Reference: USGA 2020 RoH 6.1
        return handicap_index * (slope / 113) + (rating - par)

    def compute_score_differential(self, rating: float, slope: int, score: int, playing_conditions_correction: float = 0.0):
        # Reference: USGA 2020 RoH 5.1
        score_diff = (113 / slope) * (score - rating - playing_conditions_correction)
        return round(score_diff * 10, 1) # rounded to nearest tenth, toward zero

    def compute_handicap_index(self, record: List[float]) -> float:
        # Reference: USGA 2020 RoH 5.2
        return self.maximum_handicap_index # TODO: Implement handicap index calculation

    def maximum_handicap_index(self) -> float:
        # Reference: USGA 2020 RoH 5.3
        return 54.0
