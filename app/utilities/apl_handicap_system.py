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
        self, par: int, stroke_index: int, course_handicap: int = None
    ) -> int:
        whs = WorldHandicapSystem()
        return whs.compute_hole_maximum_score(
            par=par, stroke_index=stroke_index, course_handicap=course_handicap * 2
        )

    def compute_hole_maximum_strokes(self, par: int, handicap_strokes: int) -> int:
        """
        Computes maximum strokes allowed per league rules: double par + handicap strokes

        This is separate from the maximum score for handicapping purposes.

        Parameters
        ----------
        par : int
            hole par
        handicap_strokes : int
            number of handicap strokes given to the relevant golfer on this hole

        Returns
        -------
        max_strokes : int
            maximum number of strokes allowed per league rules: double par + handicap strokes

        """
        return 2 * par + handicap_strokes

    def get_handicap_allowance(self, is_shamble: bool = False) -> float:
        """
        Determines the handicap allowance for a round given the type of event being played.

        Returns
        -------
        allowance : float
            scaling factor for handicaps in this scoring mode, in range [0, 1]

        """
        if is_shamble:
            return 0.7
        return 1.0
