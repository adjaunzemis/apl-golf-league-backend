import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api import app
from app.dependencies import get_sql_db_session, get_current_user
from app.models.course import Course
from app.models.track import Track
from app.models.tee import Tee, TeeGender
from app.models.hole import Hole
from app.models.user import User

async def override_get_current_user():
    return User(username="test_user", is_admin=True, disabled=False)

app.dependency_overrides[get_current_user] = override_get_current_user

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
    "name, year, address, phone, website",
    [
        (
            "Test Course Name",
            2021,
            "Test Street, Test City, ST 12345",
            "123-456-7890",
            "google.com",
        ),
        (
            "Test Course Name",
            2021,
            "Test Street, Test City, ST 12345",
            "123-456-7890",
            None,
        ),
        (
            "Test Course Name",
            2021,
            "Test Street, Test City, ST 12345",
            None,
            "google.com",
        ),
        ("Test Course Name", 2021, None, "123-456-7890", "google.com"),
    ],
)
def test_create_course(
    client: TestClient, name: str, year: int, address: str, phone: str, website: str
):
    app.dependency_overrides[get_current_user] = override_get_current_user # force admin user

    response = client.post(
        "/courses/",
        json={
            "name": name,
            "year": year,
            "address": address,
            "phone": phone,
            "website": website,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == name
    assert data["address"] == address
    assert data["phone"] == phone
    assert data["website"] == website
    assert data["id"] is not None
    
    app.dependency_overrides = {} # remove dependency overrides

def test_create_course_unauthorized(client: TestClient):
    response = client.post(
        "/courses/",
        json={
            "name": "Test Course",
            "year": 2021,
            "address": "Test Street, Test City, ST 12345",
            "phone": "123-456-7890",
            "website": "google.com",
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize(
    "name, year, address, phone, website",
    [
        (None, 2021, "Test Street, Test City, ST 12345", "123-456-7890", "google.com"),
        (
            "Test Course Name",
            None,
            "Test Street, Test City, ST 12345",
            "123-456-7890",
            "google.com",
        ),
    ],
)
def test_create_course_incomplete(
    client: TestClient, name: str, year: int, address: str, phone: str, website: str
):
    app.dependency_overrides[get_current_user] = override_get_current_user # force admin user
    
    response = client.post(
        "/courses/",
        json={
            "name": name,
            "year": year,
            "address": address,
            "phone": phone,
            "website": website,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    app.dependency_overrides = {} # remove dependency overrides


@pytest.mark.parametrize(
    "name, year, address, phone, website",
    [
        (
            {"key": "value"},
            2021,
            "Test Street, Test City, ST 12345",
            "123-456-7890",
            "google.com",
        ),
        (
            "Test Course Name",
            {"key": "value"},
            "Test Street, Test City, ST 12345",
            "123-456-7890",
            "google.com",
        ),
        ("Test Course Name", 2021, {"key": "value"}, "123-456-7890", "google.com"),
        (
            "Test Course Name",
            2021,
            "Test Street, Test City, ST 12345",
            {"key": "value"},
            "google.com",
        ),
        (
            "Test Course Name",
            2021,
            "Test Street, Test City, ST 12345",
            "123-456-7890",
            {"key": "value"},
        ),
    ],
)
def test_create_course_invalid(
    client: TestClient, name: str, year: int, address: str, phone: str, website: str
):
    app.dependency_overrides[get_current_user] = override_get_current_user # force admin user

    response = client.post(
        "/courses/",
        json={"name": name, "address": address, "phone": phone, "website": website},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    app.dependency_overrides = {} # remove dependency overrides


def test_read_courses(session: Session, client: TestClient):
    courses = [
        Course(
            name="Test Course 1",
            year=2021,
            address="Test Address 1",
            phone="111-111-1111",
            website="google.com",
        ),
        Course(
            name="Test Course 2",
            year=2021,
            address="Test Address 2",
            phone="222-222-2222",
            website="bing.com",
        ),
    ]
    for course in courses:
        session.add(course)
    session.commit()

    response = client.get("/courses/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == len(courses)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == courses[dIdx].name
        assert data[dIdx]["year"] == courses[dIdx].year
        assert data[dIdx]["address"] == courses[dIdx].address
        assert data[dIdx]["phone"] == courses[dIdx].phone
        assert data[dIdx]["website"] == courses[dIdx].website
        assert data[dIdx]["id"] == courses[dIdx].id


def test_read_course(session: Session, client: TestClient):
    course = Course(
        name="Test Course 1",
        year=2021,
        address="Test Address 1",
        phone="111-111-1111",
        website="google.com",
    )
    session.add(course)
    session.commit()

    response = client.get(f"/courses/{course.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == course.name
    assert data["year"] == course.year
    assert data["address"] == course.address
    assert data["phone"] == course.phone
    assert data["website"] == course.website
    assert data["id"] == course.id
    assert len(data["tracks"]) == 0


def test_delete_course(session: Session, client: TestClient):
    app.dependency_overrides[get_current_user] = override_get_current_user

    course = Course(
        name="Test Course 1",
        year=2021,
        address="Test Address 1",
        phone="111-111-1111",
        website="google.com",
    )
    session.add(course)
    session.commit()

    response = client.delete(f"/courses/{course.id}")
    assert response.status_code == status.HTTP_200_OK

    course_db = session.get(Course, course.id)
    assert course_db is None
    
    app.dependency_overrides = {} # remove dependency overrides


def test_read_tracks(session: Session, client: TestClient):
    tracks = [
        Track(name="Test Track 1", course_id=1),
        Track(name="Test Track 2", course_id=1),
    ]
    for track in tracks:
        session.add(track)
    session.commit()

    response = client.get("/courses/tracks/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == len(tracks)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == tracks[dIdx].name
        assert data[dIdx]["course_id"] == tracks[dIdx].course_id
        assert data[dIdx]["id"] == tracks[dIdx].id


def test_read_track(session: Session, client: TestClient):
    track = Track(name="Test Track 1", course_id=1)
    session.add(track)
    session.commit()

    response = client.get(f"/courses/tracks/{track.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == track.name
    assert data["course_id"] == track.course_id
    assert data["id"] == track.id
    assert len(data["tees"]) == 0


def test_update_track(session: Session, client: TestClient):
    track = Track(name="Test Track 1", course_id=1)
    session.add(track)
    session.commit()

    response = client.patch(
        f"/courses/tracks/{track.id}", json={"name": "Awesome Track"}
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == "Awesome Track"
    assert data["course_id"] == track.course_id
    assert data["id"] == track.id


def test_delete_track(session: Session, client: TestClient):
    app.dependency_overrides[get_current_user] = override_get_current_user

    track = Track(name="Test Track 1", course_id=1)
    session.add(track)
    session.commit()

    response = client.delete(f"/courses/tracks/{track.id}")
    assert response.status_code == status.HTTP_200_OK

    track_db = session.get(Track, track.id)
    assert track_db is None

    app.dependency_overrides = {} # remove dependency overrides

def test_read_tees(session: Session, client: TestClient):
    tees = [
        Tee(
            name="Test Tee 1",
            gender=TeeGender.MENS,
            rating=72.3,
            slope=128,
            color="Blue",
            track_id=1,
        ),
        Tee(
            name="Test Tee 2",
            gender=TeeGender.LADIES,
            rating=68.7,
            slope=117,
            color="Red",
            track_id=1,
        ),
    ]
    for tee in tees:
        session.add(tee)
    session.commit()

    response = client.get("/courses/tees/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == len(tees)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == tees[dIdx].name
        assert data[dIdx]["gender"] == tees[dIdx].gender
        assert data[dIdx]["rating"] == tees[dIdx].rating
        assert data[dIdx]["slope"] == tees[dIdx].slope
        assert data[dIdx]["color"] == tees[dIdx].color
        assert data[dIdx]["track_id"] == tees[dIdx].track_id
        assert data[dIdx]["id"] == tees[dIdx].id


def test_read_tee(session: Session, client: TestClient):
    tee = Tee(
        name="Test Tee 1", gender=TeeGender.MENS, rating=72.3, slope=128, color="Blue", track_id=1
    )
    session.add(tee)
    session.commit()

    response = client.get(f"/courses/tees/{tee.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == tee.name
    assert data["gender"] == tee.gender
    assert data["rating"] == tee.rating
    assert data["slope"] == tee.slope
    assert data["color"] == tee.color
    assert data["track_id"] == tee.track_id
    assert data["id"] == tee.id
    assert len(data["holes"]) == 0


def test_update_tee(session: Session, client: TestClient):
    tee = Tee(
        name="Test Tee 1", gender=TeeGender.MENS, rating=72.3, slope=128, color="Blue", track_id=1
    )
    session.add(tee)
    session.commit()

    response = client.patch(f"/courses/tees/{tee.id}", json={"name": "Awesome Tee"})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["name"] == "Awesome Tee"
    assert data["gender"] == tee.gender
    assert data["rating"] == tee.rating
    assert data["slope"] == tee.slope
    assert data["color"] == tee.color
    assert data["track_id"] == tee.track_id
    assert data["id"] == tee.id


def test_delete_tee(session: Session, client: TestClient):
    tee = Tee(
        name="Test Tee 1", gender=TeeGender.MENS, rating=72.3, slope=128, color="Blue", track_id=1
    )
    session.add(tee)
    session.commit()

    response = client.delete(f"/courses/tees/{tee.id}")
    assert response.status_code == status.HTTP_200_OK

    tee_db = session.get(Tee, tee.id)
    assert tee_db is None


def test_read_holes(session: Session, client: TestClient):
    holes = [
        Hole(number=1, par=4, yardage=385, stroke_index=3, tee_id=1),
        Hole(number=2, par=5, yardage=495, stroke_index=15, tee_id=1),
    ]
    for hole in holes:
        session.add(hole)
    session.commit()

    response = client.get("/courses/holes/")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == len(holes)
    for dIdx in range(len(data)):
        assert data[dIdx]["number"] == holes[dIdx].number
        assert data[dIdx]["par"] == holes[dIdx].par
        assert data[dIdx]["yardage"] == holes[dIdx].yardage
        assert data[dIdx]["stroke_index"] == holes[dIdx].stroke_index
        assert data[dIdx]["tee_id"] == holes[dIdx].tee_id
        assert data[dIdx]["id"] == holes[dIdx].id


def test_read_hole(session: Session, client: TestClient):
    hole = Hole(number=1, par=4, yardage=385, stroke_index=3, tee_id=1)
    session.add(hole)
    session.commit()

    response = client.get(f"/courses/holes/{hole.id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["number"] == hole.number
    assert data["par"] == hole.par
    assert data["yardage"] == hole.yardage
    assert data["stroke_index"] == hole.stroke_index
    assert data["tee_id"] == hole.tee_id
    assert data["id"] == hole.id


def test_update_hole(session: Session, client: TestClient):
    hole = Hole(number=1, par=4, yardage=385, stroke_index=3, tee_id=1)
    session.add(hole)
    session.commit()

    response = client.patch(f"/courses/holes/{hole.id}", json={"number": 3})
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["number"] == 3
    assert data["par"] == hole.par
    assert data["yardage"] == hole.yardage
    assert data["stroke_index"] == hole.stroke_index
    assert data["tee_id"] == hole.tee_id
    assert data["id"] == hole.id


def test_read_course_with_data(session: Session, client: TestClient):
    course = Course(
        name="Test Course",
        year=2021,
        address="Test Street, Test City, ST 12345",
        phone="123-456-7890",
        website="google.com",
    )
    session.add(course)
    session.commit()

    track = Track(name="Test Track", course_id=course.id)
    session.add(track)
    session.commit()

    tee = Tee(
        name="Test Tee",
        gender=TeeGender.MENS,
        rating=72.3,
        slope=128,
        color="Blue",
        track_id=track.id,
    )
    session.add(tee)
    session.commit()

    holes = [
        Hole(number=1, par=4, yardage=385, stroke_index=9, tee_id=tee.id),
        Hole(number=2, par=4, yardage=385, stroke_index=8, tee_id=tee.id),
        Hole(number=3, par=4, yardage=385, stroke_index=7, tee_id=tee.id),
        Hole(number=4, par=4, yardage=385, stroke_index=6, tee_id=tee.id),
        Hole(number=5, par=4, yardage=385, stroke_index=5, tee_id=tee.id),
        Hole(number=6, par=3, yardage=175, stroke_index=4, tee_id=tee.id),
        Hole(number=7, par=3, yardage=175, stroke_index=3, tee_id=tee.id),
        Hole(number=8, par=5, yardage=495, stroke_index=2, tee_id=tee.id),
        Hole(number=9, par=5, yardage=495, stroke_index=1, tee_id=tee.id),
    ]
    for hole in holes:
        session.add(hole)
    session.commit()

    response = client.get(f"/courses/{course.id}")
    assert response.status_code == status.HTTP_200_OK

    course_data = response.json()
    assert course_data["name"] == course.name
    assert course_data["year"] == course.year
    assert course_data["address"] == course.address
    assert course_data["phone"] == course.phone
    assert course_data["website"] == course.website
    assert course_data["id"] == course.id
    assert len(course_data["tracks"]) == 1

    track_data = course_data["tracks"][0]
    assert track_data["name"] == track.name
    assert track_data["course_id"] == track.course_id
    assert track_data["course_id"] == course.id
    assert track_data["id"] == track.id
    assert len(track_data["tees"]) == 1

    tee_data = track_data["tees"][0]
    assert tee_data["name"] == tee.name
    assert tee_data["gender"] == tee.gender
    assert tee_data["rating"] == tee.rating
    assert tee_data["slope"] == tee.slope
    assert tee_data["color"] == tee.color
    assert tee_data["track_id"] == tee.track_id
    assert tee_data["track_id"] == track.id
    assert tee_data["id"] == tee.id
    assert len(tee_data["holes"]) == 9

    for hIdx in range(len(tee_data["holes"])):
        hole_data = tee_data["holes"][hIdx]
        assert hole_data["number"] == holes[hIdx].number
        assert hole_data["par"] == holes[hIdx].par
        assert hole_data["yardage"] == holes[hIdx].yardage
        assert hole_data["stroke_index"] == holes[hIdx].stroke_index
        assert hole_data["tee_id"] == holes[hIdx].tee_id
        assert hole_data["tee_id"] == tee.id
        assert hole_data["id"] == holes[hIdx].id
