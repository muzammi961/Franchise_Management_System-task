import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.franchise import Franchise
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Create super admin
    admin = User(
        email="admin@test.com",
        password=hash_password("Admin@1234"),
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.flush()

    fuser = User(
        email="franchise@test.com",
        password=hash_password("Franchise@1234"),
        role=UserRole.FRANCHISE,
        is_active=True,
    )
    db.add(fuser)
    db.flush()

    franchise = Franchise(
        user_id=fuser.id,
        name="Test Franchise",
        phone="9999999999",
        address="123 Test Street",
        franchise_code="FRAN-TEST-001",
    )
    db.add(franchise)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin@1234",
    })
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


@pytest_asyncio.fixture
async def franchise_token(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "franchise@test.com",
        "password": "Franchise@1234",
        "franchise_code": "FRAN-TEST-001",
    })
    assert response.status_code == 200
    return response.json()["data"]["access_token"]
