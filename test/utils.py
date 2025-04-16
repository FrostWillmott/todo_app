
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from todo_app.database import Base
from todo_app.dependencies import get_db
from todo_app.main import app
from todo_app.models import Todos, Users
from todo_app.routers.auth import bcrypt_context, get_current_user

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
TEST_PASSWORD = "test_password"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "test_username", "id": 1, "user_role": "admin"}



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    db.query(Todos).delete()
    db.commit()

@pytest.fixture
def test_user():
    user = Users(
        username="test_username",
        email="test@email.com",
        first_name="test_first_name",
        last_name="test_last_name",
        hashed_password=bcrypt_context.hash(TEST_PASSWORD),
        role="admin",
        phone_number="(111)-111-1111",
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    db.query(Users).delete()
    db.commit()
