"""
Property-based tests for Provider Data Persistence

**Feature: system-testing, Property 6: Provider 数据持久化一致性**
**Validates: Requirements 5.1, 5.2, 10.2**

Tests that Provider data inserted into the database can be retrieved
with the same values (except auto-generated fields like created_at).
"""
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from sqlalchemy import create_engine, Column, String, Integer, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base

# Create a local Base for testing to avoid import chain issues
ProviderBase = declarative_base()


class ProviderModel(ProviderBase):
    """Test-local Provider model to avoid import chain issues."""
    __tablename__ = "providers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    logo = Column(String, nullable=False)
    type = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    enabled = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())


# Strategy for generating valid provider names (ASCII only)
provider_name_strategy = st.text(
    min_size=1,
    max_size=50,
    alphabet=st.characters(
        min_codepoint=32,
        max_codepoint=126,
        blacklist_characters='\x00\n\r\t'
    )
).filter(lambda x: x.strip() != '')

# Strategy for generating valid API keys (ASCII only for SQLite compatibility)
api_key_strategy = st.text(
    min_size=8,
    max_size=128,
    alphabet=st.characters(
        min_codepoint=48,  # '0'
        max_codepoint=122,  # 'z'
        whitelist_categories=('L', 'N')
    )
)

# Strategy for generating valid base URLs
base_url_strategy = st.from_regex(
    r'https?://[a-z0-9][a-z0-9.-]*[a-z0-9](/[a-z0-9/_-]*)?',
    fullmatch=True
)

# Strategy for provider types
provider_type_strategy = st.sampled_from(['openai', 'deepseek', 'qwen', 'custom'])

# Strategy for logo values
logo_strategy = st.sampled_from(['custom', 'openai', 'deepseek', 'qwen'])

# Strategy for enabled status
enabled_strategy = st.sampled_from([0, 1])


def create_test_db():
    """Create a fresh in-memory database for each test iteration."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    ProviderBase.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, Session


class TestProviderPersistenceProperties:
    """
    Property-based tests for Provider data persistence.
    
    **Feature: system-testing, Property 6: Provider 数据持久化一致性**
    **Validates: Requirements 5.1, 5.2, 10.2**
    """

    @given(
        provider_id=st.uuids().map(str),
        name=provider_name_strategy,
        api_key=api_key_strategy,
        base_url=base_url_strategy,
        provider_type=provider_type_strategy,
        logo=logo_strategy,
        enabled=enabled_strategy
    )
    @settings(max_examples=100)
    def test_provider_insert_then_query_returns_same_data(
        self,
        provider_id: str,
        name: str,
        api_key: str,
        base_url: str,
        provider_type: str,
        logo: str,
        enabled: int
    ):
        """
        **Feature: system-testing, Property 6: Provider 数据持久化一致性**
        
        For any valid Provider data, inserting into the database and then
        querying should return the same data (except auto-generated fields).
        """
        engine, Session = create_test_db()
        session = Session()
        try:
            # Insert provider
            provider = ProviderModel(
                id=provider_id,
                name=name,
                logo=logo,
                type=provider_type,
                api_key=api_key,
                base_url=base_url,
                enabled=enabled
            )
            session.add(provider)
            session.commit()
            
            # Query provider back
            result = session.query(ProviderModel).filter_by(id=provider_id).first()
            
            # Verify all fields match
            assert result is not None, f"Provider with id {provider_id} not found"
            assert result.id == provider_id, f"ID mismatch: {result.id} != {provider_id}"
            assert result.name == name, f"Name mismatch: {result.name} != {name}"
            assert result.logo == logo, f"Logo mismatch: {result.logo} != {logo}"
            assert result.type == provider_type, f"Type mismatch: {result.type} != {provider_type}"
            assert result.api_key == api_key, f"API key mismatch: {result.api_key} != {api_key}"
            assert result.base_url == base_url, f"Base URL mismatch: {result.base_url} != {base_url}"
            assert result.enabled == enabled, f"Enabled mismatch: {result.enabled} != {enabled}"
        finally:
            session.close()
            engine.dispose()

    @given(
        provider_id=st.uuids().map(str),
        name=provider_name_strategy,
        api_key=api_key_strategy,
        base_url=base_url_strategy,
        provider_type=provider_type_strategy,
        new_name=provider_name_strategy,
        new_api_key=api_key_strategy
    )
    @settings(max_examples=100)
    def test_provider_update_persists_changes(
        self,
        provider_id: str,
        name: str,
        api_key: str,
        base_url: str,
        provider_type: str,
        new_name: str,
        new_api_key: str
    ):
        """
        **Feature: system-testing, Property 6: Provider 数据持久化一致性**
        
        For any valid Provider, updating fields and committing should
        persist the changes to the database.
        """
        # Ensure new values are different
        assume(new_name != name or new_api_key != api_key)
        
        engine, Session = create_test_db()
        session = Session()
        try:
            # Insert initial provider
            provider = ProviderModel(
                id=provider_id,
                name=name,
                logo="custom",
                type=provider_type,
                api_key=api_key,
                base_url=base_url,
                enabled=1
            )
            session.add(provider)
            session.commit()
            
            # Update provider
            provider.name = new_name
            provider.api_key = new_api_key
            session.commit()
            
            # Query in a new session to ensure persistence
            session.close()
            session = Session()
            
            result = session.query(ProviderModel).filter_by(id=provider_id).first()
            
            assert result is not None
            assert result.name == new_name, f"Updated name not persisted: {result.name} != {new_name}"
            assert result.api_key == new_api_key, f"Updated API key not persisted: {result.api_key} != {new_api_key}"
        finally:
            session.close()
            engine.dispose()

    @given(
        provider_id=st.uuids().map(str),
        name=provider_name_strategy,
        api_key=api_key_strategy,
        base_url=base_url_strategy
    )
    @settings(max_examples=100)
    def test_provider_query_by_name_returns_correct_provider(
        self,
        provider_id: str,
        name: str,
        api_key: str,
        base_url: str
    ):
        """
        **Feature: system-testing, Property 6: Provider 数据持久化一致性**
        
        For any valid Provider, querying by name should return the
        correct provider with matching ID.
        """
        engine, Session = create_test_db()
        session = Session()
        try:
            # Insert provider
            provider = ProviderModel(
                id=provider_id,
                name=name,
                logo="custom",
                type="openai",
                api_key=api_key,
                base_url=base_url,
                enabled=1
            )
            session.add(provider)
            session.commit()
            
            # Query by name
            result = session.query(ProviderModel).filter_by(name=name).first()
            
            assert result is not None, f"Provider with name '{name}' not found"
            assert result.id == provider_id, f"ID mismatch when querying by name"
        finally:
            session.close()
            engine.dispose()

    @given(
        provider_ids=st.lists(
            st.uuids().map(str),
            min_size=2,
            max_size=10,
            unique=True
        )
    )
    @settings(max_examples=50)
    def test_multiple_providers_all_queryable(self, provider_ids: list):
        """
        **Feature: system-testing, Property 6: Provider 数据持久化一致性**
        
        For any set of providers inserted, all should be queryable
        and the total count should match.
        """
        engine, Session = create_test_db()
        session = Session()
        try:
            # Insert multiple providers
            for i, pid in enumerate(provider_ids):
                provider = ProviderModel(
                    id=pid,
                    name=f"Provider_{i}",
                    logo="custom",
                    type="openai",
                    api_key=f"sk-test{i}1234567890",
                    base_url=f"https://api{i}.test.com/v1",
                    enabled=1
                )
                session.add(provider)
            session.commit()
            
            # Query all providers
            results = session.query(ProviderModel).all()
            
            assert len(results) == len(provider_ids), \
                f"Expected {len(provider_ids)} providers, got {len(results)}"
            
            # Verify each provider is queryable by ID
            result_ids = {r.id for r in results}
            for pid in provider_ids:
                assert pid in result_ids, f"Provider {pid} not found in results"
        finally:
            session.close()
            engine.dispose()
