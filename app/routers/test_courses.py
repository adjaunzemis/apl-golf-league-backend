import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app
from ..dependencies import get_session
from ..models.course import Course
from ..models.track import Track
from ..models.tee import Tee
from ..models.hole import Hole

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    
@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.mark.parametrize(
    "name, location, phone, website", [
        ("Test Course Name", "Test Street, Test City, ST 12345", "123-456-7890", "google.com"),
        ("Test Course Name", "Test Street, Test City, ST 12345", "123-456-7890", None),
        ("Test Course Name", "Test Street, Test City, ST 12345", None, "google.com"),
        ("Test Course Name", None, "123-456-7890", "google.com")
    ])
def test_create_course(client: TestClient, name: str, location: str, phone: str, website: str):
    response = client.post("/courses/", json={
        "name": name, "location": location, "phone": phone, "website": website
    })
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == name
    assert data["location"] == location
    assert data["phone"] == phone
    assert data["website"] == website
    assert data["id"] is not None

def test_create_course_incomplete(client: TestClient):
    # Missing required 'name' field
    response = client.post("/courses/", json={"location": "Test Location Only"})
    assert response.status_code == 422

@pytest.mark.parametrize(
    "name, location, phone, website", [
        ({"key": "value"}, "Test Street, Test City, ST 12345", "123-456-7890", "google.com"),
        ("Test Course Name", {"key": "value"}, "123-456-7890", "google.com"),
        ("Test Course Name", "Test Street, Test City, ST 12345", {"key": "value"}, "google.com"),
        ("Test Course Name", "Test Street, Test City, ST 12345", "123-456-7890", {"key": "value"})
    ])
def test_create_course_invalid(client: TestClient, name: str, location: str, phone: str, website: str):
    # Invalid input data types
    response = client.post("/courses/", json={
        "name": name, "location": location, "phone": phone, "website": website
    })
    assert response.status_code == 422

def test_read_courses(session: Session, client: TestClient):
    courses = [
        Course(name="Test Course 1", location="Test Location 1", phone="111-111-1111", website="google.com"),
        Course(name="Test Course 2", location="Test Location 2", phone="222-222-2222", website="bing.com")
    ]
    for course in courses:
        session.add(course)
    session.commit()

    response = client.get("/courses/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == len(courses)
    for dIdx in range(len(data)):
        assert data[dIdx]["name"] == courses[dIdx].name
        assert data[dIdx]["location"] == courses[dIdx].location
        assert data[dIdx]["phone"] == courses[dIdx].phone
        assert data[dIdx]["website"] == courses[dIdx].website
        assert data[dIdx]["id"] == courses[dIdx].id

def test_read_course(session: Session, client: TestClient):
    course = Course(name="Test Course 1", location="Test Location 1", phone="111-111-1111", website="google.com")
    session.add(course)
    session.commit()

    response = client.get(f"/courses/{course.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == course.name
    assert data["location"] == course.location
    assert data["phone"] == course.phone
    assert data["website"] == course.website
    assert data["id"] == course.id

def test_update_course(session: Session, client: TestClient):
    course = Course(name="Test Course 1", location="Test Location 1", phone="111-111-1111", website="google.com")
    session.add(course)
    session.commit()

    response = client.patch(f"/courses/{course.id}", json={"name": "Awesome Course"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Awesome Course"
    assert data["location"] == course.location
    assert data["phone"] == course.phone
    assert data["website"] == course.website
    assert data["id"] == course.id

def test_delete_course(session: Session, client: TestClient):
    course = Course(name="Test Course 1", location="Test Location 1", phone="111-111-1111", website="google.com")
    session.add(course)
    session.commit()

    response = client.delete(f"/courses/{course.id}")
    assert response.status_code == 200

    course_db = session.get(Course, course.id)
    assert course_db is None

@pytest.mark.parametrize(
    "name, course_id", [
        ("Test Track Name", 1),
        ("Test Track Name", None)
    ])
def test_create_track(client: TestClient, name: str, course_id: int):
    response = client.post("/courses/tracks/", json={
        "name": name, "course_id": course_id
    })
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == name
    assert data["course_id"] == course_id
    assert data["id"] is not None

def test_create_track_incomplete(client: TestClient):
    # Missing required 'name' field
    response = client.post("/courses/tracks/", json={"course_id": 1})
    assert response.status_code == 422

@pytest.mark.parametrize(
    "name, course_id", [
        ({"key": "value"}, 1),
        ("Test Track Name", {"key": "value"})
    ])
def test_create_track_invalid(client: TestClient, name: str, course_id: int):
    # Invalid input data types
    response = client.post("/courses/tracks/", json={
        "name": name, "course_id": course_id
    })
    assert response.status_code == 422

def test_read_tracks(session: Session, client: TestClient):
    tracks = [
        Track(name="Test Track 1", course_id=1),
        Track(name="Test Track 2", course_id=1)
    ]
    for track in tracks:
        session.add(track)
    session.commit()

    response = client.get("/courses/tracks/")
    assert response.status_code == 200

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
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == track.name
    assert data["course_id"] == track.course_id
    assert data["id"] == track.id

def test_update_track(session: Session, client: TestClient):
    track = Track(name="Test Track 1", course_id=1)
    session.add(track)
    session.commit()

    response = client.patch(f"/courses/tracks/{track.id}", json={"name": "Awesome Track"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Awesome Track"
    assert data["course_id"] == track.course_id
    assert data["id"] == track.id

def test_delete_track(session: Session, client: TestClient):
    track = Track(name="Test Track 1", course_id=1)
    session.add(track)
    session.commit()

    response = client.delete(f"/courses/tracks/{track.id}")
    assert response.status_code == 200

    track_db = session.get(Track, track.id)
    assert track_db is None

@pytest.mark.parametrize(
    "name, gender, rating, slope, color, track_id", [
        ("Test Tee Name", "M", 72.3, 128, "Blue", 1),
        ("Test Tee Name", "M", 72.3, 128, "Blue", None),
        ("Test Tee Name", "M", 72.3, 128, None, 1)
    ])
def test_create_tee(client: TestClient, name: str, gender: str, rating: float, slope: int, color: str, track_id: int):
    response = client.post("/courses/tees/", json={
        "name": name, "gender": gender, "rating": rating, "slope": slope, "color": color, "track_id": track_id
    })
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == name
    assert data["gender"] == gender
    assert data["rating"] == rating
    assert data["slope"] == slope
    assert data["color"] == color
    assert data["track_id"] == track_id
    assert data["id"] is not None

@pytest.mark.parametrize(
    "name, gender, rating, slope, color, track_id", [
        (None, "M", 72.3, 128, "Blue", 1),
        ("Test Tee Name", None, 72.3, 128, "Blue", 1),
        ("Test Tee Name", "M", None, 128, "Blue", 1),
        ("Test Tee Name", "M", 72.3, None, "Blue", 1)
    ]
)
def test_create_tee_incomplete(client: TestClient, name: str, gender: str, rating: float, slope: int, color: str, track_id: int):
    # Missing required fields
    response = client.post("/courses/tees/", json={
        "name": name, "gender": gender, "rating": rating, "slope": slope, "color": color, "track_id": track_id
    })
    assert response.status_code == 422

@pytest.mark.parametrize(
    "name, gender, rating, slope, color, track_id", [
        ({"key": "value"}, "M", 72.3, 128, "Blue", 1),
        ("Test Tee Name", {"key": "value"}, 72.3, 128, "Blue", 1),
        ("Test Tee Name", "M", {"key": "value"}, 128, "Blue", 1),
        ("Test Tee Name", "M", 72.3, {"key": "value"}, "Blue", 1),
        ("Test Tee Name", "M", 72.3, 128, {"key": "value"}, 1),
        ("Test Tee Name", "M", 72.3, 128, "Blue", {"key": "value"})
    ])
def test_create_tee_invalid(client: TestClient, name: str, gender: str, rating: float, slope: int, color: str, track_id: int):
    # Invalid input data types
    response = client.post("/courses/tees/", json={
        "name": name, "gender": gender, "rating": rating, "slope": slope, "color": color, "track_id": track_id
    })
    assert response.status_code == 422

def test_read_tees(session: Session, client: TestClient):
    tees = [
        Tee(name="Test Tee 1", gender="M", rating=72.3, slope=128, color="Blue", track_id=1),
        Tee(name="Test Tee 2", gender="F", rating=68.7, slope=117, color="Red", track_id=1),
    ]
    for tee in tees:
        session.add(tee)
    session.commit()

    response = client.get("/courses/tees/")
    assert response.status_code == 200

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
    tee = Tee(name="Test Tee 1", gender="M", rating=72.3, slope=128, color="Blue", track_id=1)
    session.add(tee)
    session.commit()

    response = client.get(f"/courses/tees/{tee.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == tee.name
    assert data["gender"] == tee.gender
    assert data["rating"] == tee.rating
    assert data["slope"] == tee.slope
    assert data["color"] == tee.color
    assert data["track_id"] == tee.track_id
    assert data["id"] == tee.id

def test_update_tee(session: Session, client: TestClient):
    tee = Tee(name="Test Tee 1", gender="M", rating=72.3, slope=128, color="Blue", track_id=1)
    session.add(tee)
    session.commit()

    response = client.patch(f"/courses/tees/{tee.id}", json={"name": "Awesome Tee"})
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Awesome Tee"
    assert data["gender"] == tee.gender
    assert data["rating"] == tee.rating
    assert data["slope"] == tee.slope
    assert data["color"] == tee.color
    assert data["track_id"] == tee.track_id
    assert data["id"] == tee.id

def test_delete_track(session: Session, client: TestClient):
    tee = Tee(name="Test Tee 1", gender="M", rating=72.3, slope=128, color="Blue", track_id=1)
    session.add(tee)
    session.commit()

    response = client.delete(f"/courses/tees/{tee.id}")
    assert response.status_code == 200

    tee_db = session.get(Track, tee.id)
    assert tee_db is None
