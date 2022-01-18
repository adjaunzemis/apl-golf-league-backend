from typing import List
import numpy as np

from .world_handicap_system import WorldHandicapSystem

class APLLegacyHandicapSystem(WorldHandicapSystem):
    """
    Legacy implementation of the APL golf league handicap system.

    Similar to USGA/WHS with some adjustments for 9-hole league play.
    
    All score differentials are computed over 9-hole rounds, so the handicap
    index is a 9-hole handicap index.

    Handicap index calculation uses fewer scores from scoring record, which is
    the latest 10 score differentials.

    For maximum score per hole, uses pre-2020 USGA equitable stroke control.

    References:
    - APL Golf League Handicapping: http://aplgolfleague.com/APL_Golf/handicap.html

    """

    def compute_hole_maximum_score(self, par: int, stroke_index: int, course_handicap: int = None) -> int:
        # Reference: USGA Equitable Stroke Control (prior to 2020)
        if course_handicap <= 4:
            return par + 2
        elif course_handicap <= 9:
            return 7
        elif course_handicap <= 14:
            return 8
        elif course_handicap <= 19:
            return 9
        else:
            return 10

    def compute_hole_handicap_strokes(self, stroke_index: int, course_handicap: int) -> int:
        # Similar to WHS, but using 9-hole playing handicaps
        return super().compute_hole_handicap_strokes(stroke_index=stroke_index, course_handicap=course_handicap*2)
    
    def compute_handicap_index(self, record: List[float]) -> float:
        # Reference: APL Golf League Handicapping
        record_sorted = np.sort(record)
        if len(record) < 4:
            score_diffs_avg = record_sorted[0]
        elif len(record) < 6:
            score_diffs_avg = np.mean(record_sorted[0:2])
        elif len(record) < 8:
            score_diffs_avg = np.mean(record_sorted[0:3])
        elif len(record) < 10:
            score_diffs_avg = np.mean(record_sorted[0:4])
        else:
            score_diffs_avg = np.mean(record_sorted[0:5])
        return min(np.floor((0.96 * score_diffs_avg) * 10.0) / 10.0, self.maximum_handicap_index) # truncate to nearest tenth

    @property
    def maximum_handicap_index(self) -> float:
        # Reference: APL Golf League Handicapping
        return 30.0
