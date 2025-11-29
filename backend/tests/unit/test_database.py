"""
BiliNote Database Initialization Tests

Tests for database table structure creation and default data seeding.
Requirements: 10.1
"""
import os
import sys
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.engine import Base
from app.db.models.providers import Provider
from app.db.models.models import Model
from app.db.models.video_tasks import VideoTask


class TestDatabaseInitialization:
    """Tests for database table structure creation - Requirements 10.1"""
    
    @pytest.fixture
    def fresh_engine(self, tmp_path):
        """Create a fresh database engine for each test."""
        db_path = tmp_path / "test_init.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False
        )
        yield engine
        engine.dispose()
    
    def test_create_all_tables(self, fresh_engine):
        """Test that init_db creates all required tables."""
        # Create all tables
        Base.metadata.create_all(bind=fresh_engine)
        
        # Inspect the database
        inspector = inspect(fresh_engine)
        table_names = inspector.get_table_names()
        
        # Verify all required tables exist
        assert "providers" in table_names, "providers table should be created"
        assert "models" in table_names, "models table should be created"
        assert "video_tasks" in table_names, "video_tasks table should be created"

    
    def test_providers_table_structure(self, fresh_engine):
        """Test that providers table has correct columns."""
        Base.metadata.create_all(bind=fresh_engine)
        
        inspector = inspect(fresh_engine)
        columns = {col['name']: col for col in inspector.get_columns('providers')}
        
        # Verify required columns exist
        required_columns = ['id', 'name', 'logo', 'type', 'api_key', 'base_url', 'enabled', 'created_at']
        for col_name in required_columns:
            assert col_name in columns, f"providers table should have '{col_name}' column"
    
    def test_models_table_structure(self, fresh_engine):
        """Test that models table has correct columns."""
        Base.metadata.create_all(bind=fresh_engine)
        
        inspector = inspect(fresh_engine)
        columns = {col['name']: col for col in inspector.get_columns('models')}
        
        # Verify required columns exist
        required_columns = ['id', 'provider_id', 'model_name', 'created_at']
        for col_name in required_columns:
            assert col_name in columns, f"models table should have '{col_name}' column"
    
    def test_video_tasks_table_structure(self, fresh_engine):
        """Test that video_tasks table has correct columns."""
        Base.metadata.create_all(bind=fresh_engine)
        
        inspector = inspect(fresh_engine)
        columns = {col['name']: col for col in inspector.get_columns('video_tasks')}
        
        # Verify required columns exist
        required_columns = ['id', 'video_id', 'platform', 'task_id', 'created_at']
        for col_name in required_columns:
            assert col_name in columns, f"video_tasks table should have '{col_name}' column"


class TestDefaultDataSeeding:
    """Tests for default data seeding - Requirements 10.1"""
    
    @pytest.fixture
    def seeded_db(self, tmp_path):
        """Create a database with seeded default providers."""
        import json
        
        db_path = tmp_path / "test_seed.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False
        )
        Base.metadata.create_all(bind=engine)
        
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = TestSessionLocal()
        
        # Load builtin providers
        json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'app', 'db', 'builtin_providers.json'
        )
        
        with open(json_path, 'r', encoding='utf-8') as f:
            providers = json.load(f)
        
        # Seed providers
        for p in providers:
            session.add(Provider(
                id=p['id'],
                name=p['name'],
                api_key=p['api_key'],
                base_url=p['base_url'],
                logo=p['logo'],
                type=p['type'],
                enabled=p.get('enabled', 1)
            ))
        session.commit()
        
        yield session, providers
        
        session.close()
        engine.dispose()
    
    def test_default_providers_seeded(self, seeded_db):
        """Test that default providers are seeded correctly."""
        session, expected_providers = seeded_db
        
        # Query all providers
        providers = session.query(Provider).all()
        
        # Verify count matches
        assert len(providers) == len(expected_providers), \
            f"Expected {len(expected_providers)} providers, got {len(providers)}"
    
    def test_builtin_provider_ids(self, seeded_db):
        """Test that builtin provider IDs are correct."""
        session, expected_providers = seeded_db
        
        expected_ids = {p['id'] for p in expected_providers}
        actual_ids = {p.id for p in session.query(Provider).all()}
        
        assert expected_ids == actual_ids, \
            f"Provider IDs mismatch. Expected: {expected_ids}, Got: {actual_ids}"
    
    def test_provider_fields_populated(self, seeded_db):
        """Test that provider fields are populated correctly."""
        session, _ = seeded_db
        
        # Check OpenAI provider as example
        openai = session.query(Provider).filter_by(id='openai').first()
        
        assert openai is not None, "OpenAI provider should exist"
        assert openai.name == "OpenAI"
        assert openai.type == "built-in"
        assert openai.base_url == "https://api.openai.com/v1"
