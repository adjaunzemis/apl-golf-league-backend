from app.utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem
from app.utilities.world_handicap_system import WorldHandicapSystem


class APLHandicapSystem(APLLegacyHandicapSystem):
    """
    Current (as of 2022) implementation of the APL golf league handicap system.
    Adjustments from legacy APL golf league handicap system:
    - For handicapping maximum score per hole, uses WHS equitable stroke control.
    - Adds pace-of-play maximum score rule: double par + handicap strokes

    Similar to USGA/WHS with some adjustments for 9-hole league play.

    All score differentials are computed over 9-hole rounds, so the handicap
    index is a 9-hole handicap index.

    Handicap index calculation uses fewer scores from scoring record, which is
    the latest 10 score differentials.

    References:
    - APL Golf League Handicapping: http://aplgolfleague.com/APL_Golf/handicap.html

    """

    def compute_hole_maximum_score(
        self, par: int, stroke_index: int, course_handicap: int | None = None
    ) -> int:
        whs = WorldHandicapSystem()  # TODO: Don't re-instantiate WHS each call
        return whs.compute_hole_maximum_score(
            par=par,
            stroke_index=stroke_index,
            course_handicap=course_handicap * 2
            if course_handicap is not None
            else None,
        )
