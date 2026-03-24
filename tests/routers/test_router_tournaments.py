from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models.division import Division
from app.models.tournament_division_link import TournamentDivisionLink


def test_update_tournament_divisions_sync(client_admin: TestClient, session: Session):
    # 1. Create a tournament with two divisions
    tournament_data = {
        "name": "Initial Tournament",
        "year": 2025,
        "date": "2025-05-01T08:00:00",
        "course_id": 1,
        "divisions": [
            {"name": "Div A", "gender": "Men's", "primary_tee_id": 1},
            {"name": "Div B", "gender": "Men's", "primary_tee_id": 1},
        ],
        "secretary": "Sec",
    }
    response = client_admin.post("/tournaments/", json=tournament_data)
    assert response.status_code == status.HTTP_200_OK
    tournament_id = response.json()["id"]

    # Verify initial divisions
    links = session.exec(
        select(TournamentDivisionLink).where(
            TournamentDivisionLink.tournament_id == tournament_id
        )
    ).all()
    assert len(links) == 2

    # 2. Update the tournament: Remove Div A, Keep Div B, Add Div C
    div_b_id = next(
        link.division_id
        for link in links
        if session.get(Division, link.division_id).name == "Div B"
    )

    update_data = {
        "id": tournament_id,
        "name": "Updated Tournament",
        "year": 2025,
        "date": "2025-05-01T08:00:00",
        "course_id": 1,
        "divisions": [
            {
                "id": div_b_id,
                "name": "Div B Updated",
                "gender": "Men's",
                "primary_tee_id": 1,
            },
            {"name": "Div C", "gender": "Men's", "primary_tee_id": 1},
        ],
        "secretary": "Sec",
    }

    response = client_admin.put(f"/tournaments/{tournament_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK

    # 3. Verify divisions after update
    session.expire_all()
    links = session.exec(
        select(TournamentDivisionLink).where(
            TournamentDivisionLink.tournament_id == tournament_id
        )
    ).all()

    division_names = [session.get(Division, link.division_id).name for link in links]
    assert "Div A" not in division_names
    assert "Div B Updated" in division_names
    assert "Div C" in division_names
    assert len(links) == 2
