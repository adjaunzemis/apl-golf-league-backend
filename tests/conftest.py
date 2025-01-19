import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api import app
from app.dependencies import get_current_user, get_sql_db_session
from app.models.user import User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client_unauthorized")
def unauthorized_client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_sql_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_non_admin")
def non_admin_client_fixture(session: Session):
    def get_session_override():
        return session

    def get_current_user_override():
        return User(username="test_user", is_admin=False, disabled=False)

    app.dependency_overrides[get_sql_db_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_admin")
def admin_client_fixture(session: Session):
    def get_session_override():
        return session

    def get_current_user_override():
        return User(username="test_user", is_admin=True, disabled=False)

    app.dependency_overrides[get_sql_db_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
