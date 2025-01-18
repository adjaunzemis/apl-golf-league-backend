from datetime import date
from typing import Union

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.golfer import Golfer, GolferAffiliation
from app.models.hole import Hole
from app.models.hole_result import (
    HoleResultValidationRequest,
    HoleResultValidationResponse,
)
from app.models.round import (
    Round,
    RoundSubmissionResponse,
    RoundType,
    RoundValidationRequest,
    RoundValidationResponse,
    ScoringType,
)
from app.models.round_golfer_link import RoundGolferLink
from app.models.tee import Tee, TeeGender
from app.utilities.apl_handicap_system import APLHandicapSystem


@pytest.fixture()
def round_validate_data_valid():
    return {
        "course_handicap": 12,
        "date_played": date.today().isoformat(),
        "holes": [
            {"number": 1, "par": 4, "stroke_index": 1, "gross_score": 5},
            {"number": 2, "par": 3, "stroke_index": 9, "gross_score": 7},
            {"number": 3, "par": 5, "stroke_index": 5, "gross_score": 11},
        ],
    }


@pytest.fixture()
def round_validate_data_invalid():
    return {
        "course_handicap": 12,
        "date_played": date.today().isoformat(),
        "holes": [
            {"number": 1, "par": 4, "stroke_index": 1, "gross_score": 11},
            {"number": 2, "par": 3, "stroke_index": 9, "gross_score": 0},
            {"number": 3, "par": 5, "stroke_index": 7, "gross_score": 12},
        ],
    }


def check_validated_hole_response(
    hole_request: HoleResultValidationRequest,
    hole_response: HoleResultValidationResponse,
    course_handicap: int,
    ahs: APLHandicapSystem,
) -> None:
    assert hole_response.number == hole_request.number
    assert hole_response.par == hole_request.par
    assert hole_response.stroke_index == hole_request.stroke_index

    assert hole_response.gross_score == hole_request.gross_score

    request_handicap_strokes = ahs.compute_hole_handicap_strokes(
        hole_request.stroke_index, course_handicap
    )
    assert hole_response.handicap_strokes == request_handicap_strokes

    request_adjusted_gross_score = ahs.compute_hole_adjusted_gross_score(
        hole_request.par,
        hole_request.stroke_index,
        hole_request.gross_score,
        course_handicap,
    )
    assert hole_response.adjusted_gross_score == request_adjusted_gross_score

    assert (
        hole_response.net_score == hole_request.gross_score - request_handicap_strokes
    )

    assert hole_response.max_gross_score == ahs.compute_hole_maximum_strokes(
        hole_request.par, request_handicap_strokes
    )


def check_validated_round_response(
    round_request: RoundValidationRequest,
    round_response: RoundValidationResponse,
    ahs: APLHandicapSystem,
) -> None:
    assert round_request.date_played == round_response.date_played
    assert round_request.course_handicap == round_response.course_handicap

    for hole_idx, hole_response in enumerate(round_response.holes):
        check_validated_hole_response(
            hole_request=round_request.holes[hole_idx],
            hole_response=hole_response,
            course_handicap=round_response.course_handicap,
            ahs=ahs,
        )


def test_validate_round_valid(
    client_admin: TestClient, round_validate_data_valid: dict
):
    """Replicates `test_scoring.py::test_validate_round()` for valid round using API endpoint."""
    response = client_admin.post(f"/rounds/validate/", json=round_validate_data_valid)
    assert response.status_code == status.HTTP_200_OK

    round_request = RoundValidationRequest(**round_validate_data_valid)
    round_response = RoundValidationResponse(**response.json())

    check_validated_round_response(
        round_request=round_request,
        round_response=round_response,
        ahs=APLHandicapSystem(),
    )

    assert round_response.is_valid
    for hole_response in round_response.holes:
        assert hole_response.is_valid


def test_validate_round_invalid(
    client_admin: TestClient, round_validate_data_invalid: dict
):
    """Replicates `test_scoring.py::test_validate_round()` for invalid round using API endpoint."""
    response = client_admin.post(f"/rounds/validate/", json=round_validate_data_invalid)
    assert response.status_code == status.HTTP_200_OK

    round_request = RoundValidationRequest(**round_validate_data_invalid)
    round_response = RoundValidationResponse(**response.json())

    check_validated_round_response(
        round_request=round_request,
        round_response=round_response,
        ahs=APLHandicapSystem(),
    )

    assert not round_response.is_valid
    for hole_response in round_response.holes:
        assert not hole_response.is_valid


def test_submit_round(
    session: Session, client_admin: TestClient, round_validate_data_valid: dict
):
    """Tests nominal response from submitting valid round data."""
    # Initialize database contents
    session.add(
        Golfer(id=1, name="Test Golfer", affiliation=GolferAffiliation.APL_EMPLOYEE)
    )
    session.add(Tee(id=1, name="Test", gender=TeeGender.MENS, rating=72.3, slope=123))
    for hole_idx, hole in enumerate(round_validate_data_valid["holes"]):
        session.add(
            Hole(
                id=hole_idx + 1,
                tee_id=1,
                number=hole["number"],
                par=hole["par"],
                stroke_index=hole["stroke_index"],
            )
        )
    session.commit()

    # Submit round data
    round_submit_data = {
        **round_validate_data_valid,
        "golfer_id": 1,
        "tee_id": 1,
        "round_type": RoundType.FLIGHT,
        "scoring_type": ScoringType.INDIVIDUAL,
    }
    response = client_admin.post(f"/rounds/submit/", json=round_submit_data)

    assert response.status_code == status.HTTP_200_OK

    # Check database updates
    round_response = RoundSubmissionResponse(**response.json())

    round_db = session.get(Round, round_response.round_id)
    assert round_db.id == round_response.round_id
    assert round_db.golfers[0].id == 1
    assert round_db.tee_id == 1
    assert round_db.type == RoundType.FLIGHT
    assert round_db.scoring_type == ScoringType.INDIVIDUAL

    for hole_idx, hole_result_db in enumerate(round_db.hole_results):
        assert (
            hole_result_db.hole.number == round_submit_data["holes"][hole_idx]["number"]
        )
        assert hole_result_db.hole.par == round_submit_data["holes"][hole_idx]["par"]
        assert (
            hole_result_db.hole.stroke_index
            == round_submit_data["holes"][hole_idx]["stroke_index"]
        )
        assert (
            hole_result_db.gross_score
            == round_submit_data["holes"][hole_idx]["gross_score"]
        )

    golfer_db = session.get(Golfer, round_response.golfer_id)
    assert golfer_db.id == 1

    tee_db = session.get(Tee, round_response.tee_id)
    assert tee_db.id == 1

    round_golfer_link_db = session.exec(
        select(RoundGolferLink)
        .where(RoundGolferLink.golfer_id == round_response.golfer_id)
        .where(RoundGolferLink.round_id == round_response.round_id)
    ).one()
    assert round_golfer_link_db.playing_handicap == round_submit_data["course_handicap"]


def test_submit_round_unauthorized(
    session: Session, client_unauthorized: TestClient, round_validate_data_valid: dict
):
    """Tests error from unauthorized user attempting to submit round data."""
    # Submit round data
    round_submit_data = {
        **round_validate_data_valid,
        "golfer_id": 1,
        "tee_id": 1,
        "round_type": RoundType.FLIGHT,
        "scoring_type": ScoringType.INDIVIDUAL,
    }
    response = client_unauthorized.post(f"/rounds/submit/", json=round_submit_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_submit_round_invalid(
    client_admin: TestClient, round_validate_data_invalid: dict
):
    """Tests error response from submitting invalid round data."""
    round_submit_data = {
        **round_validate_data_invalid,
        "golfer_id": 1,
        "tee_id": 1,
        "round_type": RoundType.FLIGHT,
        "scoring_type": ScoringType.INDIVIDUAL,
    }
    response = client_admin.post(f"/rounds/submit/", json=round_submit_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cannot submit round with invalid scoring" in response.json()["detail"]


@pytest.mark.parametrize(
    "golfer_id, tee_id, round_type, scoring_type, expected_status, expected_detail",
    [
        (
            99,
            1,
            RoundType.FLIGHT,
            ScoringType.INDIVIDUAL,
            status.HTTP_404_NOT_FOUND,
            ["Golfer", "not found"],
        ),
        (
            1,
            99,
            RoundType.FLIGHT,
            ScoringType.INDIVIDUAL,
            status.HTTP_404_NOT_FOUND,
            ["Expected", "found", "in database for tee"],
        ),
        (
            1,
            1,
            "invalid",
            ScoringType.INDIVIDUAL,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            None,
        ),
        (1, 1, RoundType.FLIGHT, "invalid", status.HTTP_422_UNPROCESSABLE_ENTITY, None),
    ],
)
def test_submit_round_error(
    session: Session,
    client_admin: TestClient,
    round_validate_data_valid: dict,
    golfer_id: int,
    tee_id: int,
    round_type: RoundType,
    scoring_type: ScoringType,
    expected_status: int,
    expected_detail: Union[list[str], None],
):
    """Tests error responses from submitting round data."""
    # Initialize database contents
    session.add(
        Golfer(id=1, name="Test Golfer", affiliation=GolferAffiliation.APL_EMPLOYEE)
    )
    session.add(Tee(id=1, name="Test", gender=TeeGender.MENS, rating=72.3, slope=123))
    for hole_idx, hole in enumerate(round_validate_data_valid["holes"]):
        session.add(
            Hole(
                id=hole_idx + 1,
                tee_id=1,
                number=hole["number"],
                par=hole["par"],
                stroke_index=hole["stroke_index"],
            )
        )
    session.commit()

    # Submit round data
    round_submit_data = {
        **round_validate_data_valid,
        "golfer_id": golfer_id,
        "tee_id": tee_id,
        "round_type": round_type,
        "scoring_type": scoring_type,
    }
    response = client_admin.post(f"/rounds/submit/", json=round_submit_data)

    assert response.status_code == expected_status

    if expected_detail is not None:
        assert all([detail in response.json()["detail"] for detail in expected_detail])
