from typing import List
import numpy as np

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
            return -int(-course_handicap > (18 - stroke_index))
        return int(course_handicap / 18) + int(course_handicap % 18 >= stroke_index)

    def compute_course_handicap(self, par: int, rating: float, slope: int, handicap_index: float) -> float:
        # Reference: USGA 2020 RoH 6.1
        return handicap_index * (slope / 113) + (rating - par)

    def compute_score_differential(self, rating: float, slope: int, score: int, playing_conditions_correction: float = 0.0):
        # Reference: USGA 2020 RoH 5.1
        score_diff = (113 / slope) * (score - rating - playing_conditions_correction)
        return np.round(score_diff, 1) # round to nearest tenth

    def compute_handicap_index(self, record: List[float]) -> float:
        # Reference: USGA 2020 RoH 5.2, 5.3, 5.8
        record_sorted = np.sort(record)
        if len(record_sorted) < 4:
            handicap_index = record_sorted[0] - 2.0
        elif len(record_sorted) < 5:
            handicap_index = record_sorted[0] - 1.0
        elif len(record_sorted) < 6:
            handicap_index = record_sorted[0]
        elif len(record_sorted) < 7:
            handicap_index = np.mean(record_sorted[0:2]) - 1.0
        elif len(record_sorted) < 9:
            handicap_index = np.mean(record_sorted[0:2])
        elif len(record_sorted) < 12:
            handicap_index = np.mean(record_sorted[0:3])
        elif len(record_sorted) < 15:
            handicap_index = np.mean(record_sorted[0:4])
        elif len(record_sorted) < 17:
            handicap_index = np.mean(record_sorted[0:5])
        elif len(record_sorted) < 19:
            handicap_index = np.mean(record_sorted[0:6])
        elif len(record_sorted) < 20:
            handicap_index = np.mean(record_sorted[0:7])
        else:
            handicap_index = np.mean(record_sorted[0:8])
        # TODO: Add soft/hard cap logic, see USGA 2020 RoH 5.8
        return np.round(min(handicap_index, self.maximum_handicap_index), 1) # round to nearest tenth

    @property
    def maximum_handicap_index(self) -> float:
        # Reference: USGA 2020 RoH 5.3
        return 54.0
