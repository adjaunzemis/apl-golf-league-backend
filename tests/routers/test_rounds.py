import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from typing import Dict, List
from datetime import date


from app.api import app
from app.dependencies import get_sql_db_session
from app.models.round import Round, RoundValidationRequest, RoundValidationResponse
from app.models.hole_result import HoleResult
from app.utilities.apl_handicap_system import APLHandicapSystem


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_sql_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "tee_id, golfer_id, handicap_index, playing_handicap, date_played",
    [(1, 1, 12.3, 12, str(date.today()))],
)
def test_create_round(
    client: TestClient,
    tee_id: int,
    golfer_id: int,
    handicap_index: float,
    playing_handicap: int,
    date_played: date,
):
    response = client.post(
        "/rounds/",
        json={
            "tee_id": tee_id,
            "golfer_id": golfer_id,
            "handicap_index": handicap_index,
            "playing_handicap": playing_handicap,
            "date_played": date_played,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["tee_id"] == tee_id
    assert data["golfer_id"] == golfer_id
    assert data["handicap_index"] == handicap_index
    assert data["playing_handicap"] == playing_handicap
    assert data["date_played"] == date_played
    assert data["id"] is not None


@pytest.mark.parametrize(
    "tee_id, golfer_id, handicap_index, playing_handicap, date_played",
    [
        (1, 1, 12.3, 12, None),
        (1, 1, 12.3, None, str(date.today())),
        (1, 1, None, 12, str(date.today())),
        (1, None, 12.3, 12, str(date.today())),
        (None, 1, 12.3, 12, str(date.today())),
    ],
)
def test_create_round_incomplete(
    client: TestClient,
    tee_id: int,
    golfer_id: int,
    handicap_index: float,
    playing_handicap: int,
    date_played: date,
):
    # Missing required fields
    response = client.post(
        "/rounds/",
        json={
            "tee_id": tee_id,
            "golfer_id": golfer_id,
            "handicap_index": handicap_index,
            "playing_handicap": playing_handicap,
            "date_played": date_played,
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "tee_id, golfer_id, handicap_index, playing_handicap, date_played",
    [
        ({"key": "value"}, 1, 12.3, 12, str(date.today())),
        (1, {"key": "value"}, 12.3, 12, str(date.today())),
        (1, 1, {"key": "value"}, 12, str(date.today())),
        (1, 1, 12.3, {"key": "value"}, str(date.today())),
        (1, 1, 12.3, 12, {"key": "value"}),
    ],
)
def test_create_round_invalid(
    client: TestClient,
    tee_id: int,
    golfer_id: int,
    handicap_index: float,
    playing_handicap: int,
    date_played: date,
):
    response = client.post(
        "/rounds/",
        json={
            "tee_id": tee_id,
            "golfer_id": golfer_id,
            "handicap_index": handicap_index,
            "playing_handicap": playing_handicap,
            "date_played": date_played,
        },
    )
    assert response.status_code == 422


def test_read_rounds(session: Session, client: TestClient):
    rounds = [
        Round(
            tee_id=1,
            golfer_id=1,
            handicap_index=12.3,
            playing_handicap=12,
            date_played=date.today(),
        ),
        Round(
            tee_id=2,
            golfer_id=2,
            handicap_index=18.6,
            playing_handicap=17,
            date_played=date.today(),
        ),
    ]
    for round in rounds:
        session.add(round)
    session.commit()

    response = client.get("/rounds/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(rounds)
    for dIdx in range(len(data)):
        assert data[dIdx]["tee_id"] == rounds[dIdx].tee_id
        assert data[dIdx]["golfer_id"] == rounds[dIdx].golfer_id
        assert data[dIdx]["handicap_index"] == rounds[dIdx].handicap_index
        assert data[dIdx]["playing_handicap"] == rounds[dIdx].playing_handicap
        assert data[dIdx]["date_played"] == str(rounds[dIdx].date_played)
        assert data[dIdx]["id"] == rounds[dIdx].id


def test_read_round(session: Session, client: TestClient):
    round = Round(
        tee_id=1,
        golfer_id=1,
        handicap_index=12.3,
        playing_handicap=12,
        date_played=date.today(),
    )
    session.add(round)
    session.commit()

    response = client.get(f"/rounds/{round.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["tee_id"] == round.tee_id
    assert data["golfer_id"] == round.golfer_id
    assert data["handicap_index"] == round.handicap_index
    assert data["playing_handicap"] == round.playing_handicap
    assert data["date_played"] == str(round.date_played)
    assert data["id"] == round.id


def test_update_round(session: Session, client: TestClient):
    round = Round(
        tee_id=1,
        golfer_id=1,
        handicap_index=12.3,
        playing_handicap=12,
        date_played=date.today(),
    )
    session.add(round)
    session.commit()

    response = client.patch(f"/rounds/{round.id}", json={"golfer_id": 2, "tee_id": 3})
    assert response.status_code == 200

    data = response.json()
    assert data["tee_id"] == 3
    assert data["golfer_id"] == 2
    assert data["handicap_index"] == round.handicap_index
    assert data["playing_handicap"] == round.playing_handicap
    assert data["date_played"] == str(round.date_played)
    assert data["id"] == round.id


def test_delete_round(session: Session, client: TestClient):
    round = Round(
        tee_id=1,
        golfer_id=1,
        handicap_index=12.3,
        playing_handicap=12,
        date_played=date.today(),
    )
    session.add(round)
    session.commit()

    response = client.delete(f"/rounds/{round.id}")
    assert response.status_code == 200

    round_db = session.get(Round, round.id)
    assert round_db is None


@pytest.mark.parametrize("round_id, hole_id, strokes", [(1, 1, 4)])
def test_create_hole_result(
    client: TestClient, round_id: int, hole_id: int, strokes: int
):
    response = client.post(
        "/rounds/hole_results/",
        json={"round_id": round_id, "hole_id": hole_id, "strokes": strokes},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["round_id"] == round_id
    assert data["hole_id"] == hole_id
    assert data["strokes"] == strokes
    assert data["id"] is not None


@pytest.mark.parametrize(
    "round_id, hole_id, strokes",
    [
        (1, 1, None),
        (1, None, 4),
        (None, 1, 4),
    ],
)
def test_create_hole_result_incomplete(
    client: TestClient, round_id: int, hole_id: int, strokes: int
):
    # Missing required fields
    response = client.post(
        "/rounds/hole_results/",
        json={"round_id": round_id, "hole_id": hole_id, "strokes": strokes},
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "round_id, hole_id, strokes",
    [
        (1, 1, {"key": "value"}),
        (1, {"key": "value"}, 4),
        ({"key": "value"}, 1, 4),
    ],
)
def test_create_hole_result_invalid(
    client: TestClient, round_id: int, hole_id: int, strokes: int
):
    response = client.post(
        "/rounds/hole_results/",
        json={"round_id": round_id, "hole_id": hole_id, "strokes": strokes},
    )
    assert response.status_code == 422


def test_read_hole_results(session: Session, client: TestClient):
    hole_results = [
        HoleResult(round_id=1, hole_id=1, strokes=4),
        HoleResult(round_id=1, hole_id=2, strokes=5),
    ]
    for hole_result in hole_results:
        session.add(hole_result)
    session.commit()

    response = client.get("/rounds/hole_results/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(hole_results)
    for dIdx in range(len(data)):
        assert data[dIdx]["round_id"] == hole_results[dIdx].round_id
        assert data[dIdx]["hole_id"] == hole_results[dIdx].hole_id
        assert data[dIdx]["strokes"] == hole_results[dIdx].strokes
        assert data[dIdx]["id"] == hole_results[dIdx].id


def test_read_hole_result(session: Session, client: TestClient):
    hole_result = HoleResult(round_id=1, hole_id=1, strokes=4)
    session.add(hole_result)
    session.commit()

    response = client.get(f"/rounds/hole_results/{hole_result.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["round_id"] == hole_result.round_id
    assert data["hole_id"] == hole_result.hole_id
    assert data["strokes"] == hole_result.strokes
    assert data["id"] == hole_result.id


def test_update_hole_result(session: Session, client: TestClient):
    hole_result = HoleResult(round_id=1, hole_id=1, strokes=4)
    session.add(hole_result)
    session.commit()

    response = client.patch(
        f"/rounds/hole_results/{hole_result.id}", json={"strokes": 5}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["round_id"] == hole_result.round_id
    assert data["hole_id"] == hole_result.hole_id
    assert data["strokes"] == 5
    assert data["id"] == hole_result.id


def test_delete_hole_result(session: Session, client: TestClient):
    hole_result = HoleResult(round_id=1, hole_id=1, strokes=4)
    session.add(hole_result)
    session.commit()

    response = client.delete(f"/rounds/hole_results/{hole_result.id}")
    assert response.status_code == 200

    hole_result_db = session.get(HoleResult, hole_result.id)
    assert hole_result_db is None


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
    session: Session,
    client: TestClient,
    round_request_data: Dict,
    hole_is_valid: List[bool],
):
    """Replicates `test_scoring.py::test_validate_round()` using API endpoint."""
    response = client.post(f"/rounds/validate/", json=round_request_data)
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
