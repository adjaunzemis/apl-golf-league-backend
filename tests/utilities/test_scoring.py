from datetime import date

import pytest

from app.models.match import MatchHoleResult, MatchHoleWinner, MatchValidationRequest
from app.models.round import RoundValidationRequest
from app.utilities import scoring
from app.utilities.apl_handicap_system import APLHandicapSystem
from tests.utilities import load_fixture


@pytest.mark.parametrize(
    "round_request_data, hole_is_valid",
    [
        (
            {
                "course_handicap": 12,
                "date_played": date.today().isoformat(),
                "holes": [
                    {"number": 1, "par": 4, "stroke_index": 1, "gross_score": 5},
                    {"number": 2, "par": 3, "stroke_index": 9, "gross_score": 7},
                    {"number": 3, "par": 5, "stroke_index": 5, "gross_score": 11},
                ],
            },
            [True, True, True],
        ),
        (
            {
                "course_handicap": 12,
                "date_played": date.today().isoformat(),
                "holes": [
                    {"number": 1, "par": 4, "stroke_index": 1, "gross_score": 11},
                    {"number": 2, "par": 3, "stroke_index": 9, "gross_score": 0},
                    {"number": 3, "par": 5, "stroke_index": 7, "gross_score": 12},
                ],
            },
            [False, False, False],
        ),
        (
            {
                "course_handicap": 6,
                "date_played": date(year=2023, month=7, day=19),
                "holes": [
                    {"number": 1, "par": 4, "stroke_index": 7, "gross_score": 7},
                    {"number": 2, "par": 4, "stroke_index": 5, "gross_score": 4},
                    {"number": 3, "par": 4, "stroke_index": 1, "gross_score": 7},
                    {"number": 4, "par": 4, "stroke_index": 11, "gross_score": 9},
                    {"number": 5, "par": 3, "stroke_index": 3, "gross_score": 4},
                    {"number": 6, "par": 4, "stroke_index": 9, "gross_score": 4},
                    {"number": 7, "par": 4, "stroke_index": 13, "gross_score": 6},
                    {"number": 8, "par": 3, "stroke_index": 17, "gross_score": 4},
                    {"number": 9, "par": 5, "stroke_index": 15, "gross_score": 4},
                ],
            },
            [True, True, True, True, True, True, True, True, True],
        ),
    ],
)
def test_validate_round(
    round_request_data: dict,
    hole_is_valid: list[bool],
):
    round_request = RoundValidationRequest(**round_request_data)
    round_response = scoring.validate_round(round_request)

    ahs = APLHandicapSystem()
    for hole_idx, hole_response in enumerate(round_response.holes):
        assert hole_response.number == round_request.holes[hole_idx].number
        assert hole_response.par == round_request.holes[hole_idx].par
        assert hole_response.stroke_index == round_request.holes[hole_idx].stroke_index
        assert hole_response.gross_score == round_request.holes[hole_idx].gross_score
        handicap_strokes = ahs.compute_hole_handicap_strokes(
            round_request.holes[hole_idx].stroke_index, round_request.course_handicap
        )
        assert hole_response.handicap_strokes == handicap_strokes
        assert (
            hole_response.adjusted_gross_score
            == ahs.compute_hole_adjusted_gross_score(
                round_request.holes[hole_idx].par,
                round_request.holes[hole_idx].stroke_index,
                round_request.holes[hole_idx].gross_score,
                round_request.course_handicap,
            )
        )
        assert (
            hole_response.net_score
            == round_request.holes[hole_idx].gross_score - handicap_strokes
        )
        assert hole_response.max_gross_score == ahs.compute_hole_maximum_strokes(
            round_request.holes[hole_idx].par, handicap_strokes
        )
        assert hole_response.is_valid == hole_is_valid[hole_idx]

    assert round_response.is_valid == all(hole_is_valid)


def test_validate_match():
    match_request = MatchValidationRequest(
        **load_fixture("valid_match/match_request.json")
    )
    match_hole_results = [
        MatchHoleResult(**result)
        for result in load_fixture("valid_match/match_hole_results.json")
    ]

    match_response = scoring.validate_match(match_request)

    assert match_response.home_team_score == 6.5
    assert match_response.away_team_score == 4.5

    for idx, hole_result in enumerate(match_response.hole_results):
        expected_result = match_hole_results[idx]
        assert (
            hole_result.home_team_gross_score == expected_result.home_team_gross_score
        )
        assert hole_result.home_team_net_score == expected_result.home_team_net_score
        assert (
            hole_result.home_team_handicap_strokes
            == expected_result.home_team_handicap_strokes
        )
        assert (
            hole_result.away_team_gross_score == expected_result.away_team_gross_score
        )
        assert hole_result.away_team_net_score == expected_result.away_team_net_score
        assert (
            hole_result.away_team_handicap_strokes
            == expected_result.away_team_handicap_strokes
        )
        assert hole_result.winner == expected_result.winner

    assert match_response.is_valid


@pytest.mark.parametrize(
    "hole_winners, home_net_scores, away_net_scores, date_played, expected_home_score, expected_away_score",
    [
        (
            [MatchHoleWinner.HOME] * 9,
            [36, 27],
            [36, 36],
            date.today(),
            11.0,
            0.0,
        ),
        (
            [MatchHoleWinner.AWAY] * 9,
            [36, 36],
            [36, 27],
            date.today(),
            0.0,
            11.0,
        ),
        (
            [MatchHoleWinner.TIE] * 9,
            [36, 36],
            [36, 36],
            date.today(),
            5.5,
            5.5,
        ),
        (
            [
                MatchHoleWinner.TIE,
                MatchHoleWinner.AWAY,
                MatchHoleWinner.AWAY,
                MatchHoleWinner.HOME,
                MatchHoleWinner.AWAY,
                MatchHoleWinner.AWAY,
                MatchHoleWinner.HOME,
                MatchHoleWinner.HOME,
                MatchHoleWinner.HOME,
            ],
            [42, 40],
            [43, 44],
            date(year=2023, month=5, day=3),
            6.5,
            4.5,
        ),
    ],
)
def test_compute_match_score(
    hole_winners: list[MatchHoleWinner],
    home_net_scores: list[int],
    away_net_scores: list[int],
    date_played: date,
    expected_home_score: float,
    expected_away_score: float,
):
    (home_score, away_score) = scoring.compute_match_score(
        hole_winners=hole_winners,
        home_net_scores=home_net_scores,
        away_net_scores=away_net_scores,
        date_played=date_played,
    )
    assert home_score == expected_home_score
    assert away_score == expected_away_score
