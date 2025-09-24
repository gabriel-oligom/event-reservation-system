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
from app.database import Base

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
    transaction = connection.begin() #
    session = TestingSessionLocal(bind=connection)
    try:
        yield session # pause here and give the access to the DB session
    finally:
        session.close()
        transaction.rollback()
        connection.close()