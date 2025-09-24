# ── Core Concepts ─────────────────────────────────────────────
# - conftest.py: special file auto-loaded by pytest for shared setup
# - fixture: reusable setup logic for tests (DB session, client)
# - scope="session": fixture runs once per test session
# - autouse=True: fixture runs automatically without being called
# ─────────────────────────────────────────────────────────────

import os
import time
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(dotenv_path=".env.test")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") # Load test DB URL from .env.test (not committed to git)
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL not set. Check or create a .env.test file and load it before running pytest.")

# Override DATABASE_URL for test environment (to ensure it all for safety)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def initialize_test_db():
    """
    Execute only once per pytest session
    - Create all the tables (Base.metadata.create_all) in the test database
    - Do a 'Base.metadata.drop_all' to clean it all after the tests
    """

    # wait for test DB to be 
    retries = 20
    while retries:
        try:
            conn = engine.connect()
            conn.close()
            break
        except Exception:
            time.sleep(1)
            retries -= 1
        if retries == 0:
            raise RuntimeError("TimedOut waiting for test Postgres to be ready at " + TEST_DATABASE_URL)
        
    # Import Base here to ensure DATABASE_URL is set and the DB is ready before SQLAlchemy initializes.
    # DATABASE_URL is overridden with TEST_DATABASE_URL before imports, so Base uses the test DB.
    from app.database import Base 
        
    # Create tables in test database
    Base.metadata.create_all(bind=engine)
    yield # pause here, run the tests, then come back to clean up
    # Clean up final
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """
    For each test:
    - Opens a DB connection and starts a transaction.
    - Yields a session bound to that connection.
    - Rolls back after the test to keep the DB clean.
    """
    connection = engine.connect()
    transaction = connection.begin() # starts a DB transaction so all changes made during the test can be rolled back afterward, keeping the DB clean.

    session = TestingSessionLocal(bind=connection)
    try:
        yield session # pause here and give the access to the DB session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    """
    Overrides the app's get_db dependency to use the test database session (db_session).
    This ensures all requests made through TestClient interact with a controlled test database.
    """

    from app.main import app
    from app.database import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Overrides get_db so all Depends(get_db) use the test session (db_session) during testing.
    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()