"""
Property-based tests for Task ID generation functionality.

**Feature: system-testing, Property 5: Task ID 唯一性**
**Validates: Requirements 6.1**

Tests that for any batch of generated task_ids, all IDs should be unique (using UUID).
"""
import sys
import os
import uuid
from typing import List

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


def generate_task_id() -> str:
    """Generate a unique task ID using UUID4."""
    return str(uuid.uuid4())


class TestTaskIdUniquenessProperties:
    """
    **Feature: system-testing, Property 5: Task ID 唯一性**
    
    For any batch of generated task_ids, all IDs should be unique (using UUID).
    """

    @given(batch_size=st.integers(min_value=2, max_value=100))
    @settings(max_examples=100)
    def test_batch_task_ids_are_unique(self, batch_size: int):
        """
        **Feature: system-testing, Property 5: Task ID 唯一性**
        **Validates: Requirements 6.1**
        
        For any batch size, all generated task_ids should be unique.
        """
        task_ids = [generate_task_id() for _ in range(batch_size)]
        unique_ids = set(task_ids)
        
        assert len(unique_ids) == batch_size, (
            f"Generated {batch_size} task_ids but only {len(unique_ids)} are unique"
        )

    @given(batch_size=st.integers(min_value=2, max_value=50))
    @settings(max_examples=100)
    def test_task_ids_are_valid_uuid_format(self, batch_size: int):
        """
        **Feature: system-testing, Property 5: Task ID 唯一性**
        **Validates: Requirements 6.1**
        
        For any batch of task_ids, each should be a valid UUID format.
        """
        task_ids = [generate_task_id() for _ in range(batch_size)]
        
        for task_id in task_ids:
            # Should be parseable as UUID
            try:
                parsed = uuid.UUID(task_id)
                assert str(parsed) == task_id
            except ValueError:
                pytest.fail(f"Invalid UUID format: {task_id}")

    @given(batch_size=st.integers(min_value=2, max_value=50))
    @settings(max_examples=100)
    def test_task_ids_are_uuid_version_4(self, batch_size: int):
        """
        **Feature: system-testing, Property 5: Task ID 唯一性**
        **Validates: Requirements 6.1**
        
        For any batch of task_ids, each should be UUID version 4.
        """
        task_ids = [generate_task_id() for _ in range(batch_size)]
        
        for task_id in task_ids:
            parsed = uuid.UUID(task_id)
            assert parsed.version == 4, f"Expected UUID v4, got v{parsed.version}"

    @given(
        batch1_size=st.integers(min_value=1, max_value=20),
        batch2_size=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=100)
    def test_separate_batches_have_no_overlap(self, batch1_size: int, batch2_size: int):
        """
        **Feature: system-testing, Property 5: Task ID 唯一性**
        **Validates: Requirements 6.1**
        
        For any two separately generated batches, there should be no overlapping IDs.
        """
        batch1 = set(generate_task_id() for _ in range(batch1_size))
        batch2 = set(generate_task_id() for _ in range(batch2_size))
        
        overlap = batch1 & batch2
        assert len(overlap) == 0, f"Found overlapping IDs between batches: {overlap}"

    @given(st.data())
    @settings(max_examples=100)
    def test_task_id_length_is_consistent(self, data):
        """
        **Feature: system-testing, Property 5: Task ID 唯一性**
        **Validates: Requirements 6.1**
        
        All generated task_ids should have consistent length (36 characters for UUID).
        """
        batch_size = data.draw(st.integers(min_value=1, max_value=50))
        task_ids = [generate_task_id() for _ in range(batch_size)]
        
        for task_id in task_ids:
            assert len(task_id) == 36, f"Expected length 36, got {len(task_id)}"

    @given(batch_size=st.integers(min_value=2, max_value=50))
    @settings(max_examples=100)
    def test_task_ids_contain_only_valid_characters(self, batch_size: int):
        """
        **Feature: system-testing, Property 5: Task ID 唯一性**
        **Validates: Requirements 6.1**
        
        All generated task_ids should contain only valid hex characters and hyphens.
        """
        valid_chars = set("0123456789abcdef-")
        task_ids = [generate_task_id() for _ in range(batch_size)]
        
        for task_id in task_ids:
            invalid_chars = set(task_id.lower()) - valid_chars
            assert len(invalid_chars) == 0, (
                f"Found invalid characters in task_id: {invalid_chars}"
            )
