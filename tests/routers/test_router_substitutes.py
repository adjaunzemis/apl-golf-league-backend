import pytest
from fastapi import status
from sqlmodel import Session

from app.models.substitutes import Substitute


@pytest.fixture()
def session_with_substitutes(session: Session):
    session.add(Substitute(flight_id=1, golfer_id=1, division_id=1))
    session.add(Substitute(flight_id=1, golfer_id=2, division_id=1))
    session.add(Substitute(flight_id=2, golfer_id=3, division_id=1))
    session.commit()
    yield session


def test_get_substitutes(session_with_substitutes, client_unauthorized):
    response = client_unauthorized.get("/substitutes/")
    assert response.status_code == status.HTTP_200_OK
    substitutes_api = [
        Substitute(**substitute_json) for substitute_json in response.json()
    ]
    assert len(substitutes_api) == 3


def test_get_substitutes_for_flight(session_with_substitutes, client_unauthorized):
    response = client_unauthorized.get("/substitutes/?flight_id=1")
    assert response.status_code == status.HTTP_200_OK
    substitutes_api = [
        Substitute(**substitute_json) for substitute_json in response.json()
    ]
    assert len(substitutes_api) == 2
    for substitute_api in substitutes_api:
        assert substitute_api.flight_id == 1


def test_get_substitutes_for_flight_empty(
    session_with_substitutes, client_unauthorized
):
    response = client_unauthorized.get("/substitutes/?flight_id=3")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


def test_create_substitute(session_with_substitutes, client_unauthorized):
    response = client_unauthorized.post(
        "/substitutes/", json={"flight_id": 1, "golfer_id": 5, "division_id": 1}
    )
    assert response.status_code == status.HTTP_200_OK
    substitute_api = Substitute(**response.json())
    assert substitute_api.flight_id == 1
    assert substitute_api.golfer_id == 5
    assert substitute_api.division_id == 1


def test_create_substitute_duplicate(session_with_substitutes, client_admin):
    response = client_admin.post(
        "/substitutes/", json={"flight_id": 1, "golfer_id": 1, "division_id": 1}
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_delete_substitute_unauthorized(session_with_substitutes, client_unauthorized):
    response = client_unauthorized.delete("/substitutes/?flight_id=1&golfer_id=2")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_substitute_non_admin(session_with_substitutes, client_non_admin):
    response = client_non_admin.delete("/substitutes/?flight_id=1&golfer_id=2")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_substitute(session_with_substitutes, client_admin):
    response = client_admin.delete("/substitutes/?flight_id=1&golfer_id=2")
    assert response.status_code == status.HTTP_200_OK
    active_substitute_api = Substitute(**response.json())
    assert active_substitute_api.flight_id == 1
    assert active_substitute_api.golfer_id == 2


def test_delete_substitute_not_found(session_with_substitutes, client_admin):
    response = client_admin.delete("/substitutes/?flight_id=1&golfer_id=5")
    assert response.status_code == status.HTTP_404_NOT_FOUND
