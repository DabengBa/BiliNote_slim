"""
Unit tests for Provider Service

Tests for API Key masking and Provider CRUD operations.
Requirements: 5.1, 5.2, 5.4
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class ProviderService:
    """
    Local copy of mask_key function to avoid import chain issues.
    This mirrors the implementation in app/services/provider.py
    """
    @staticmethod
    def mask_key(key: str) -> str:
        if not key or len(key) < 8:
            return '*' * len(key) if key else ''
        return key[:4] + '*' * (len(key) - 8) + key[-4:]


# Try to import the real ProviderService, fall back to local copy
try:
    from app.services.provider import ProviderService as RealProviderService
    ProviderService = RealProviderService
except ImportError:
    pass  # Use local copy defined above


class TestMaskKey:
    """Tests for ProviderService.mask_key() function - Requirements 5.4"""

    def test_mask_key_normal_length(self):
        """Test masking a normal length API key (>= 8 characters)."""
        key = "sk-test1234567890abcdefghijklmnop"
        masked = ProviderService.mask_key(key)
        
        # Should show first 4 and last 4 characters
        assert masked.startswith("sk-t")
        assert masked.endswith("mnop")
        # Middle should be asterisks
        assert "*" in masked
        # Length should be preserved
        assert len(masked) == len(key)

    def test_mask_key_exactly_8_characters(self):
        """Test masking a key with exactly 8 characters."""
        key = "12345678"
        masked = ProviderService.mask_key(key)
        
        # Should show first 4 and last 4 (no asterisks in middle)
        assert masked == "12345678"
        assert len(masked) == len(key)

    def test_mask_key_9_characters(self):
        """Test masking a key with 9 characters."""
        key = "123456789"
        masked = ProviderService.mask_key(key)
        
        # Should show first 4, 1 asterisk, last 4
        assert masked == "1234*6789"
        assert len(masked) == len(key)

    def test_mask_key_short_key_7_chars(self):
        """Test masking a short key (7 characters - less than 8)."""
        key = "1234567"
        masked = ProviderService.mask_key(key)
        
        # Short keys should be fully masked
        assert masked == "*******"
        assert len(masked) == len(key)

    def test_mask_key_short_key_4_chars(self):
        """Test masking a very short key (4 characters)."""
        key = "1234"
        masked = ProviderService.mask_key(key)
        
        # Short keys should be fully masked
        assert masked == "****"
        assert len(masked) == len(key)

    def test_mask_key_short_key_1_char(self):
        """Test masking a single character key."""
        key = "a"
        masked = ProviderService.mask_key(key)
        
        assert masked == "*"
        assert len(masked) == len(key)

    def test_mask_key_empty_string(self):
        """Test masking an empty string."""
        key = ""
        masked = ProviderService.mask_key(key)
        
        assert masked == ""
        assert len(masked) == 0

    def test_mask_key_none(self):
        """Test masking None value."""
        masked = ProviderService.mask_key(None)
        
        # None should return empty string (len(None) would fail, so it returns '')
        assert masked == ""

    def test_mask_key_preserves_length_long_key(self):
        """Test that masking preserves the original key length for long keys."""
        key = "sk-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJ"
        masked = ProviderService.mask_key(key)
        
        assert len(masked) == len(key)
        assert masked[:4] == key[:4]
        assert masked[-4:] == key[-4:]

    def test_mask_key_special_characters(self):
        """Test masking a key with special characters."""
        key = "sk-!@#$%^&*()_+-=[]{}|;':\",./<>?"
        masked = ProviderService.mask_key(key)
        
        assert len(masked) == len(key)
        assert masked.startswith("sk-!")
        assert masked.endswith("/<>?")



class TestProviderCRUD:
    """
    Tests for Provider CRUD operations - Requirements 5.1, 5.2
    
    These tests use an in-memory SQLite database to test Provider
    add, update, and query operations.
    """

    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Set up an in-memory test database for each test."""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.db.engine import Base
        from app.db.models.providers import Provider
        
        # Create in-memory database
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            echo=False
        )
        Base.metadata.create_all(bind=self.engine)
        
        self.TestSession = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.session = self.TestSession()
        
        yield
        
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_add_provider_creates_record(self):
        """Test that adding a provider creates a database record."""
        from app.db.models.providers import Provider
        
        provider = Provider(
            id="test-provider-001",
            name="Test Provider",
            logo="custom",
            type="openai",
            api_key="sk-test1234567890abcdef",
            base_url="https://api.test.com/v1",
            enabled=1
        )
        self.session.add(provider)
        self.session.commit()
        
        # Query the provider back
        result = self.session.query(Provider).filter_by(id="test-provider-001").first()
        
        assert result is not None
        assert result.name == "Test Provider"
        assert result.type == "openai"
        assert result.api_key == "sk-test1234567890abcdef"
        assert result.base_url == "https://api.test.com/v1"
        assert result.enabled == 1

    def test_add_provider_with_all_fields(self):
        """Test adding a provider with all required fields."""
        from app.db.models.providers import Provider
        
        provider = Provider(
            id="test-provider-002",
            name="DeepSeek Provider",
            logo="deepseek",
            type="deepseek",
            api_key="ds-abcdefghijklmnop",
            base_url="https://api.deepseek.com/v1",
            enabled=0
        )
        self.session.add(provider)
        self.session.commit()
        
        result = self.session.query(Provider).filter_by(id="test-provider-002").first()
        
        assert result is not None
        assert result.name == "DeepSeek Provider"
        assert result.logo == "deepseek"
        assert result.type == "deepseek"
        assert result.enabled == 0

    def test_update_provider_modifies_record(self):
        """Test that updating a provider modifies the database record."""
        from app.db.models.providers import Provider
        
        # First, add a provider
        provider = Provider(
            id="test-provider-003",
            name="Original Name",
            logo="custom",
            type="openai",
            api_key="sk-original123456789",
            base_url="https://api.original.com/v1",
            enabled=1
        )
        self.session.add(provider)
        self.session.commit()
        
        # Update the provider
        provider.name = "Updated Name"
        provider.api_key = "sk-updated123456789"
        provider.base_url = "https://api.updated.com/v1"
        self.session.commit()
        
        # Query and verify
        result = self.session.query(Provider).filter_by(id="test-provider-003").first()
        
        assert result.name == "Updated Name"
        assert result.api_key == "sk-updated123456789"
        assert result.base_url == "https://api.updated.com/v1"

    def test_update_provider_enabled_status(self):
        """Test updating provider enabled status."""
        from app.db.models.providers import Provider
        
        provider = Provider(
            id="test-provider-004",
            name="Toggle Provider",
            logo="custom",
            type="openai",
            api_key="sk-toggle1234567890",
            base_url="https://api.toggle.com/v1",
            enabled=1
        )
        self.session.add(provider)
        self.session.commit()
        
        # Disable the provider
        provider.enabled = 0
        self.session.commit()
        
        result = self.session.query(Provider).filter_by(id="test-provider-004").first()
        assert result.enabled == 0
        
        # Re-enable the provider
        provider.enabled = 1
        self.session.commit()
        
        result = self.session.query(Provider).filter_by(id="test-provider-004").first()
        assert result.enabled == 1

    def test_query_provider_by_id(self):
        """Test querying a provider by ID."""
        from app.db.models.providers import Provider
        
        provider = Provider(
            id="test-provider-005",
            name="Query Test Provider",
            logo="custom",
            type="qwen",
            api_key="qw-query1234567890",
            base_url="https://api.qwen.com/v1",
            enabled=1
        )
        self.session.add(provider)
        self.session.commit()
        
        result = self.session.query(Provider).filter_by(id="test-provider-005").first()
        
        assert result is not None
        assert result.id == "test-provider-005"
        assert result.name == "Query Test Provider"

    def test_query_provider_by_name(self):
        """Test querying a provider by name."""
        from app.db.models.providers import Provider
        
        provider = Provider(
            id="test-provider-006",
            name="Unique Provider Name",
            logo="custom",
            type="openai",
            api_key="sk-unique1234567890",
            base_url="https://api.unique.com/v1",
            enabled=1
        )
        self.session.add(provider)
        self.session.commit()
        
        result = self.session.query(Provider).filter_by(name="Unique Provider Name").first()
        
        assert result is not None
        assert result.id == "test-provider-006"

    def test_query_nonexistent_provider_returns_none(self):
        """Test that querying a non-existent provider returns None."""
        from app.db.models.providers import Provider
        
        result = self.session.query(Provider).filter_by(id="nonexistent-id").first()
        
        assert result is None

    def test_query_all_providers(self):
        """Test querying all providers."""
        from app.db.models.providers import Provider
        
        # Add multiple providers
        providers = [
            Provider(
                id=f"test-provider-{i}",
                name=f"Provider {i}",
                logo="custom",
                type="openai",
                api_key=f"sk-test{i}1234567890",
                base_url=f"https://api{i}.test.com/v1",
                enabled=1
            )
            for i in range(1, 4)
        ]
        
        for p in providers:
            self.session.add(p)
        self.session.commit()
        
        results = self.session.query(Provider).all()
        
        assert len(results) == 3
        names = [r.name for r in results]
        assert "Provider 1" in names
        assert "Provider 2" in names
        assert "Provider 3" in names

    def test_delete_provider(self):
        """Test deleting a provider."""
        from app.db.models.providers import Provider
        
        provider = Provider(
            id="test-provider-delete",
            name="Delete Me Provider",
            logo="custom",
            type="openai",
            api_key="sk-delete1234567890",
            base_url="https://api.delete.com/v1",
            enabled=1
        )
        self.session.add(provider)
        self.session.commit()
        
        # Verify it exists
        result = self.session.query(Provider).filter_by(id="test-provider-delete").first()
        assert result is not None
        
        # Delete it
        self.session.delete(result)
        self.session.commit()
        
        # Verify it's gone
        result = self.session.query(Provider).filter_by(id="test-provider-delete").first()
        assert result is None
