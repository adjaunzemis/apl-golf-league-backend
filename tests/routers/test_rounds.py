import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.models.round import (
    RoundValidationRequest,
    RoundValidationResponse,
)
from app.utilities.apl_handicap_system import APLHandicapSystem


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
    ],
)
def test_validate_round(
    client_admin: TestClient,
    round_request_data: dict,
    hole_is_valid: list[bool],
):
    """Replicates `test_scoring.py::test_validate_round()` using API endpoint."""
    response = client_admin.post(f"/rounds/validate/", json=round_request_data)
    assert response.status_code == 200

    ahs = APLHandicapSystem()
    round_request = RoundValidationRequest(**round_request_data)
    round_response = RoundValidationResponse(**response.json())
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
