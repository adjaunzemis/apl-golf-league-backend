import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.golfer import Golfer, GolferAffiliation


@pytest.mark.parametrize(
    "name, affiliation, email, phone",
    [
        ("Test Golfer", GolferAffiliation.APL_EMPLOYEE, "test@email.com", None),
        (
            "Test Golfer",
            GolferAffiliation.APL_EMPLOYEE,
            "test@email.com",
            "123-456-7890",
        ),
    ],
)
def test_create_golfer(
    client_unauthorized: TestClient, name: str, affiliation: str, email: str, phone: str
):
    response = client_unauthorized.post(
        "/golfers/",
        json={"name": name, "affiliation": affiliation, "email": email, "phone": phone},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == name
    assert data["affiliation"] == affiliation
    assert data["email"] == email
    assert data["phone"] == phone
    assert data["id"] is not None


@pytest.mark.parametrize(
    "name, affiliation, email, phone",
    [
        (
            "Test Golfer With Name Much Too Long",
            GolferAffiliation.APL_EMPLOYEE,
            "test@email.com",
            None,
        ),
        ("A", GolferAffiliation.APL_EMPLOYEE, "test@email.com", None),
        ("!nvalid CH@RS!", GolferAffiliation.APL_EMPLOYEE, "test@email.com", None),
        ("Missing Affiliation", None, "test@email.com", None),
        ("Missing Email", GolferAffiliation.APL_EMPLOYEE, None, None),
    ],
)
def test_create_golfer_invalid(
    client_unauthorized: TestClient, name: str, affiliation: str, email: str, phone: str
):
    response = client_unauthorized.post(
        "/golfers/",
        json={"name": name, "affiliation": affiliation, "email": email, "phone": phone},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_golfer_incomplete(client_unauthorized: TestClient):
    response = client_unauthorized.post(
        "/golfers/", json={"affiliation": GolferAffiliation.NON_APL_EMPLOYEE}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "name, affiliation",
    [
        ({"key": "value"}, GolferAffiliation.NON_APL_EMPLOYEE),
        ("Test Golfer", {"key": "value"}),
        ("Test Golfer", "BAD_AFFILIATION"),
    ],
)
def test_create_golfer_invalid(
    client_unauthorized: TestClient, name: str, affiliation: str
):
    response = client_unauthorized.post(
        "/golfers/", json={"name": name, "affiliation": affiliation}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_golfers(session: Session, client_unauthorized: TestClient):
    golfers = [
        Golfer(name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE),
        Golfer(name="Test Golfer B", affiliation=GolferAffiliation.APL_EMPLOYEE),
    ]
    for golfer in golfers:
        session.add(golfer)
    session.commit()

    response = client_unauthorized.get("/golfers/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["num_golfers"] == len(golfers)
    assert len(data["golfers"]) == len(golfers)
    for dIdx in range(len(data["golfers"])):
        assert data["golfers"][dIdx]["name"] == golfers[dIdx].name
        assert data["golfers"][dIdx]["affiliation"] == golfers[dIdx].affiliation
        assert data["golfers"][dIdx]["golfer_id"] == golfers[dIdx].id


def test_read_golfer(session: Session, client_unauthorized: TestClient):
    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client_unauthorized.get(f"/golfers/{golfer.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == golfer.name
    assert data["affiliation"] == golfer.affiliation
    assert data["golfer_id"] == golfer.id


def test_update_golfer(session: Session, client_admin: TestClient):
    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client_admin.patch(f"/golfers/{golfer.id}", json={"name": "New Golfer"})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == "New Golfer"
    assert data["affiliation"] == golfer.affiliation
    assert data["id"] == golfer.id


def test_update_golfer_unauthorized(session: Session, client_unauthorized: TestClient):
    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client_unauthorized.patch(
        f"/golfers/{golfer.id}", json={"name": "New Golfer"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_golfer(session: Session, client_admin: TestClient):
    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client_admin.delete(f"/golfers/{golfer.id}")
    assert response.status_code == status.HTTP_200_OK

    golfer_db = session.get(Golfer, golfer.id)
    assert golfer_db is None


def test_delete_golfer_unauthorized(session: Session, client_unauthorized: TestClient):
    golfer = Golfer(
        name="Test Golfer A", affiliation=GolferAffiliation.NON_APL_EMPLOYEE
    )
    session.add(golfer)
    session.commit()

    response = client_unauthorized.delete(f"/golfers/{golfer.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
