import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database.session import Base, get_db
from backend.app.main import app
from backend.app.core.security import create_access_token, get_password_hash
from backend.app.models.user import User, UserRole

# In-memory SQLite for high-speed isolated unit and integration testing
TEST_DATABASE_URL = "sqlite:///./data/test_db.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_teacher(db_session):
    teacher = User(
        email="test_teacher@evalagent.com",
        hashed_password=get_password_hash("password123"),
        full_name="Prof. Test Teacher",
        role=UserRole.TEACHER,
        department="Computer Science",
        is_active=True,
    )
    db_session.add(teacher)
    db_session.commit()
    db_session.refresh(teacher)
    return teacher


@pytest.fixture
def test_student(db_session):
    student = User(
        email="test_student@evalagent.com",
        hashed_password=get_password_hash("password123"),
        full_name="Alice Student",
        role=UserRole.STUDENT,
        student_id="STU-101",
        department="Computer Science",
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def teacher_auth_headers(test_teacher):
    token = create_access_token(
        subject=test_teacher.id,
        role=test_teacher.role.value,
        email=test_teacher.email,
        full_name=test_teacher.full_name
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_auth_headers(test_student):
    token = create_access_token(
        subject=test_student.id,
        role=test_student.role.value,
        email=test_student.email,
        full_name=test_student.full_name
    )
    return {"Authorization": f"Bearer {token}"}
