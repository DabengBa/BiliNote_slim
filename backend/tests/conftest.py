"""
BiliNote Test Configuration

Provides shared pytest fixtures for unit, property, and integration tests.
"""
import os
import sys
import pytest
from typing import Generator
from unittest.mock import patch

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Hypothesis configuration
from hypothesis import settings, Verbosity, Phase

# Register hypothesis profiles
settings.register_profile(
    "default",
    max_examples=100,
    verbosity=Verbosity.normal,
    phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target],
)

settings.register_profile(
    "ci",
    max_examples=200,
    verbosity=Verbosity.normal,
)

settings.register_profile(
    "debug",
    max_examples=10,
    verbosity=Verbosity.verbose,
)

# Load default profile
settings.load_profile("default")


# Test database URL - use file-based SQLite for tests to avoid module reload issues
TEST_DATABASE_URL = "sqlite:///test_bili_note.db"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine with in-memory SQLite."""
    from sqlalchemy import create_engine
    from app.db.engine import Base
    
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session."""
    from sqlalchemy.orm import sessionmaker, Session
    
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client():
    """Create a FastAPI TestClient with test database.
    
    Uses the existing database engine but creates tables if needed.
    """
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app import create_app
    from app.db.engine import Base, engine
    from app.db.models.providers import Provider
    from app.db.models.models import Model
    from app.db.models.video_tasks import VideoTask
    
    # Create all tables in the existing database
    Base.metadata.create_all(bind=engine)
    
    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        # Minimal lifespan for testing - no external dependencies
        yield
    
    app = create_app(lifespan=test_lifespan)
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_provider() -> dict:
    """Generate sample Provider data for testing."""
    return {
        "id": "test-provider-001",
        "name": "Test Provider",
        "logo": "custom",
        "type": "openai",
        "api_key": "sk-test1234567890abcdefghijklmnop",
        "base_url": "https://api.test.com/v1",
        "enabled": 1,
    }


@pytest.fixture
def sample_provider_short_key() -> dict:
    """Generate sample Provider with short API key."""
    return {
        "id": "test-provider-002",
        "name": "Short Key Provider",
        "logo": "custom",
        "type": "openai",
        "api_key": "sk-123",
        "base_url": "https://api.test.com/v1",
        "enabled": 1,
    }


@pytest.fixture
def sample_urls() -> dict:
    """Generate sample video URLs for testing."""
    return {
        "bilibili": [
            "https://www.bilibili.com/video/BV1xx411c7mD",
            "https://bilibili.com/video/BV1234567890",
        ],
        "youtube": [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=abc123_-xyz",
        ],
        "douyin": [
            "https://www.douyin.com/video/7123456789012345678",
        ],
        "invalid": [
            "https://example.com/video/123",
            "not-a-url",
            "",
        ],
    }
