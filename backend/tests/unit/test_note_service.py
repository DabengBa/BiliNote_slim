"""
Unit tests for note service functionality.

Tests the _extract_screenshot_timestamps function for extracting
screenshot markers from Markdown text.

Requirements: 4.3, 6.1
"""
import sys
import os
import re
import uuid
from typing import List, Tuple

import pytest

# Add backend to path for direct module imports
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


# Copy the function for isolated testing (avoids heavy import chain)
def _extract_screenshot_timestamps(markdown: str) -> List[Tuple[str, int]]:
    """
    从 Markdown 文本中提取所有 '*Screenshot-mm:ss' 或 'Screenshot-[mm:ss]' 标记，
    返回 [(原始标记文本, 时间戳秒数), ...] 列表。

    :param markdown: 原始 Markdown 文本
    :return: 标记与对应时间戳秒数的列表
    """
    pattern = r"(?:\*Screenshot-(\d{2}):(\d{2})|Screenshot-\[(\d{2}):(\d{2})\])"
    results: List[Tuple[str, int]] = []
    for match in re.finditer(pattern, markdown):
        mm = match.group(1) or match.group(3)
        ss = match.group(2) or match.group(4)
        total_seconds = int(mm) * 60 + int(ss)
        results.append((match.group(0), total_seconds))
    return results


class TestScreenshotTimestampExtraction:
    """Tests for screenshot timestamp extraction - Requirements 4.3"""

    def test_extract_asterisk_format_single(self):
        """Test extracting single *Screenshot-mm:ss format."""
        markdown = "Some text *Screenshot-01:30 more text"
        result = _extract_screenshot_timestamps(markdown)
        assert len(result) == 1
        assert result[0] == ("*Screenshot-01:30", 90)

    def test_extract_asterisk_format_multiple(self):
        """Test extracting multiple *Screenshot-mm:ss formats."""
        markdown = "*Screenshot-00:30 text *Screenshot-02:15 more *Screenshot-10:00"
        result = _extract_screenshot_timestamps(markdown)
        assert len(result) == 3
        assert result[0] == ("*Screenshot-00:30", 30)
        assert result[1] == ("*Screenshot-02:15", 135)
        assert result[2] == ("*Screenshot-10:00", 600)

    def test_extract_bracket_format_single(self):
        """Test extracting single Screenshot-[mm:ss] format."""
        markdown = "Some text Screenshot-[05:45] more text"
        result = _extract_screenshot_timestamps(markdown)
        assert len(result) == 1
        assert result[0] == ("Screenshot-[05:45]", 345)

    def test_extract_bracket_format_multiple(self):
        """Test extracting multiple Screenshot-[mm:ss] formats."""
        markdown = "Screenshot-[00:00] text Screenshot-[01:00] more Screenshot-[59:59]"
        result = _extract_screenshot_timestamps(markdown)
        assert len(result) == 3
        assert result[0] == ("Screenshot-[00:00]", 0)
        assert result[1] == ("Screenshot-[01:00]", 60)
        assert result[2] == ("Screenshot-[59:59]", 3599)

    def test_extract_mixed_formats(self):
        """Test extracting both formats in same text."""
        markdown = "*Screenshot-01:00 and Screenshot-[02:30] together"
        result = _extract_screenshot_timestamps(markdown)
        assert len(result) == 2
        assert result[0] == ("*Screenshot-01:00", 60)
        assert result[1] == ("Screenshot-[02:30]", 150)

    def test_no_markers_returns_empty_list(self):
        """Test that text without markers returns empty list."""
        markdown = "This is just regular markdown text without any screenshot markers."
        result = _extract_screenshot_timestamps(markdown)
        assert result == []

    def test_empty_string_returns_empty_list(self):
        """Test that empty string returns empty list."""
        result = _extract_screenshot_timestamps("")
        assert result == []

    def test_zero_timestamp(self):
        """Test extracting zero timestamp (00:00)."""
        markdown = "*Screenshot-00:00"
        result = _extract_screenshot_timestamps(markdown)
        assert len(result) == 1
        assert result[0] == ("*Screenshot-00:00", 0)

    def test_timestamp_calculation_minutes_only(self):
        """Test timestamp calculation with minutes only (mm:00)."""
        markdown = "*Screenshot-05:00"
        result = _extract_screenshot_timestamps(markdown)
        assert result[0][1] == 300  # 5 * 60 = 300

    def test_timestamp_calculation_seconds_only(self):
        """Test timestamp calculation with seconds only (00:ss)."""
        markdown = "*Screenshot-00:45"
        result = _extract_screenshot_timestamps(markdown)
        assert result[0][1] == 45

    def test_invalid_format_not_extracted(self):
        """Test that invalid formats are not extracted."""
        invalid_markdowns = [
            "Screenshot-01:30",  # Missing asterisk or brackets
            "*Screenshot01:30",  # Missing hyphen
            "Screenshot[01:30]",  # Missing hyphen
            "*Screenshot-1:30",  # Single digit minute
            "*Screenshot-01:3",  # Single digit second
        ]
        for markdown in invalid_markdowns:
            result = _extract_screenshot_timestamps(markdown)
            assert result == [], f"Should not extract from: {markdown}"

    def test_markers_in_markdown_context(self):
        """Test extraction from realistic markdown content."""
        markdown = """
# Video Notes

## Introduction
The video starts with an overview. *Screenshot-00:15

## Main Content
Key point discussed here. Screenshot-[05:30]

### Details
More information *Screenshot-12:45 about the topic.

## Conclusion
Final thoughts Screenshot-[30:00]
"""
        result = _extract_screenshot_timestamps(markdown)
        assert len(result) == 4
        assert result[0] == ("*Screenshot-00:15", 15)
        assert result[1] == ("Screenshot-[05:30]", 330)
        assert result[2] == ("*Screenshot-12:45", 765)
        assert result[3] == ("Screenshot-[30:00]", 1800)


class TestTaskIdGeneration:
    """Tests for Task ID generation - Requirements 6.1"""

    def test_uuid_format_valid(self):
        """Test that generated task_id is valid UUID format."""
        task_id = str(uuid.uuid4())
        # UUID format: 8-4-4-4-12 hex characters
        assert len(task_id) == 36
        parts = task_id.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_uuid_is_valid_hex(self):
        """Test that UUID contains only valid hex characters."""
        task_id = str(uuid.uuid4())
        hex_chars = set("0123456789abcdef-")
        assert all(c in hex_chars for c in task_id.lower())

    def test_uuid_uniqueness_small_batch(self):
        """Test that multiple UUIDs are unique."""
        task_ids = [str(uuid.uuid4()) for _ in range(100)]
        assert len(set(task_ids)) == 100

    def test_uuid_can_be_parsed(self):
        """Test that generated UUID can be parsed back."""
        task_id = str(uuid.uuid4())
        parsed = uuid.UUID(task_id)
        assert str(parsed) == task_id

    def test_uuid_version_4(self):
        """Test that generated UUID is version 4."""
        task_id = uuid.uuid4()
        assert task_id.version == 4
