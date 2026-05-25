import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.utils.db import get_db, BASE

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture(scope="function")
def db():

    BASE.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    yield session

    session.close()

    BASE.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

    app.dependency_overrides.clear()
