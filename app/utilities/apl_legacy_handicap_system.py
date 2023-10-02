import numpy as np

from app.models.match import MatchHoleResult, MatchTeamDesignator
from app.utilities.world_handicap_system import WorldHandicapSystem


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

    def compute_hole_maximum_score(
        self, par: int, stroke_index: int, course_handicap: int = None
    ) -> int:
        # Reference: USGA Equitable Stroke Control (prior to 2020)
        # Note: This has already taken into account 9-hole course handicaps with 18-hole stroke indexes,
        # do not multiply course handicap by two!
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

    def compute_hole_handicap_strokes(
        self, stroke_index: int, course_handicap: int
    ) -> int:
        # Similar to WHS, but using 9-hole playing handicaps
        return super().compute_hole_handicap_strokes(
            stroke_index=stroke_index, course_handicap=course_handicap * 2
        )

    def compute_handicap_index(self, record: list[float]) -> float:
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
        return min(
            np.floor((0.96 * score_diffs_avg) * 10.0) / 10.0,
            self.maximum_handicap_index,
        )  # truncate to nearest tenth

    def determine_match_hole_result(
        self,
        home_team_gross_scores: list[int],
        away_team_gross_scores: list[int],
        team_receiving_handicap_strokes: MatchTeamDesignator,
        team_handicap_strokes_received: int,
    ) -> MatchHoleResult:
        if team_receiving_handicap_strokes == MatchTeamDesignator.HOME:
            home_team_net_score = (
                sum(home_team_gross_scores) - team_handicap_strokes_received
            )
            away_team_net_score = sum(away_team_gross_scores)
        else:
            away_team_net_score = sum(away_team_gross_scores)
            away_team_net_score = (
                sum(away_team_gross_scores) - team_handicap_strokes_received
            )

        if home_team_net_score < away_team_net_score:
            return MatchHoleResult.HOME
        elif away_team_net_score < home_team_net_score:
            return MatchHoleResult.AWAY
        return MatchHoleResult.TIE

    @property
    def maximum_handicap_index(self) -> float:
        # Reference: APL Golf League Handicapping
        return 30.0

    @property
    def match_points_for_winning_hole(self) -> float:
        return 1.0

    @property
    def match_points_for_tying_hole(self) -> float:
        return 0.5

    @property
    def match_points_for_losing_hole(self) -> float:
        return 0.0

    @property
    def match_points_for_winning_total_net_score(self) -> float:
        return 2.0

    @property
    def match_points_for_tying_total_net_score(self) -> float:
        return 1.0

    @property
    def match_points_for_losing_total_net_score(self) -> float:
        return 0.0
