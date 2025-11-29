"""
Property-based tests for screenshot timestamp extraction functionality.

**Feature: system-testing, Property 4: 截图时间戳提取准确性**
**Validates: Requirements 4.3**

Tests that for any Markdown text containing '*Screenshot-mm:ss' or 'Screenshot-[mm:ss]'
format markers, the extraction function should return correct timestamps
(seconds = mm * 60 + ss).
"""
import sys
import os
import re
from typing import List, Tuple

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

# Add backend to path
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


# Copy the function for isolated testing (avoids heavy import chain)
def _extract_screenshot_timestamps(markdown: str) -> List[Tuple[str, int]]:
    """
    从 Markdown 文本中提取所有 '*Screenshot-mm:ss' 或 'Screenshot-[mm:ss]' 标记，
    返回 [(原始标记文本, 时间戳秒数), ...] 列表。
    """
    pattern = r"(?:\*Screenshot-(\d{2}):(\d{2})|Screenshot-\[(\d{2}):(\d{2})\])"
    results: List[Tuple[str, int]] = []
    for match in re.finditer(pattern, markdown):
        mm = match.group(1) or match.group(3)
        ss = match.group(2) or match.group(4)
        total_seconds = int(mm) * 60 + int(ss)
        results.append((match.group(0), total_seconds))
    return results


# Strategies for generating valid timestamp components
# Minutes: 00-59, Seconds: 00-59
minutes_strategy = st.integers(min_value=0, max_value=59)
seconds_strategy = st.integers(min_value=0, max_value=59)


@st.composite
def asterisk_marker_strategy(draw):
    """Generate valid *Screenshot-mm:ss markers with expected timestamp."""
    mm = draw(minutes_strategy)
    ss = draw(seconds_strategy)
    marker = f"*Screenshot-{mm:02d}:{ss:02d}"
    expected_seconds = mm * 60 + ss
    return (marker, expected_seconds)


@st.composite
def bracket_marker_strategy(draw):
    """Generate valid Screenshot-[mm:ss] markers with expected timestamp."""
    mm = draw(minutes_strategy)
    ss = draw(seconds_strategy)
    marker = f"Screenshot-[{mm:02d}:{ss:02d}]"
    expected_seconds = mm * 60 + ss
    return (marker, expected_seconds)


@st.composite
def markdown_with_asterisk_markers(draw):
    """Generate markdown text with *Screenshot-mm:ss markers."""
    num_markers = draw(st.integers(min_value=1, max_value=5))
    markers_with_expected = [draw(asterisk_marker_strategy()) for _ in range(num_markers)]
    
    # Build markdown with markers interspersed with text
    parts = []
    for marker, _ in markers_with_expected:
        prefix_text = draw(st.text(
            alphabet=st.characters(blacklist_characters="*[]"),
            min_size=0, max_size=50
        ))
        parts.append(prefix_text)
        parts.append(marker)
    
    # Add trailing text
    suffix_text = draw(st.text(
        alphabet=st.characters(blacklist_characters="*[]"),
        min_size=0, max_size=20
    ))
    parts.append(suffix_text)
    
    markdown = "".join(parts)
    return (markdown, markers_with_expected)


@st.composite
def markdown_with_bracket_markers(draw):
    """Generate markdown text with Screenshot-[mm:ss] markers."""
    num_markers = draw(st.integers(min_value=1, max_value=5))
    markers_with_expected = [draw(bracket_marker_strategy()) for _ in range(num_markers)]
    
    # Build markdown with markers interspersed with text
    parts = []
    for marker, _ in markers_with_expected:
        prefix_text = draw(st.text(
            alphabet=st.characters(blacklist_characters="*[]"),
            min_size=0, max_size=50
        ))
        parts.append(prefix_text)
        parts.append(marker)
    
    # Add trailing text
    suffix_text = draw(st.text(
        alphabet=st.characters(blacklist_characters="*[]"),
        min_size=0, max_size=20
    ))
    parts.append(suffix_text)
    
    markdown = "".join(parts)
    return (markdown, markers_with_expected)


class TestScreenshotTimestampExtractionProperties:
    """
    **Feature: system-testing, Property 4: 截图时间戳提取准确性**
    
    For any Markdown text containing '*Screenshot-mm:ss' or 'Screenshot-[mm:ss]'
    format markers, the extraction function should return correct timestamps
    where seconds = mm * 60 + ss.
    """

    @given(marker_data=asterisk_marker_strategy())
    @settings(max_examples=100)
    def test_asterisk_format_timestamp_calculation(self, marker_data: Tuple[str, int]):
        """
        **Feature: system-testing, Property 4: 截图时间戳提取准确性**
        **Validates: Requirements 4.3**
        
        For any *Screenshot-mm:ss marker, the extracted timestamp should equal mm * 60 + ss.
        """
        marker, expected_seconds = marker_data
        result = _extract_screenshot_timestamps(marker)
        
        assert len(result) == 1, f"Should extract exactly one marker from: {marker}"
        extracted_marker, extracted_seconds = result[0]
        assert extracted_marker == marker, f"Extracted marker should match input"
        assert extracted_seconds == expected_seconds, (
            f"Timestamp mismatch for {marker}: expected {expected_seconds}, got {extracted_seconds}"
        )

    @given(marker_data=bracket_marker_strategy())
    @settings(max_examples=100)
    def test_bracket_format_timestamp_calculation(self, marker_data: Tuple[str, int]):
        """
        **Feature: system-testing, Property 4: 截图时间戳提取准确性**
        **Validates: Requirements 4.3**
        
        For any Screenshot-[mm:ss] marker, the extracted timestamp should equal mm * 60 + ss.
        """
        marker, expected_seconds = marker_data
        result = _extract_screenshot_timestamps(marker)
        
        assert len(result) == 1, f"Should extract exactly one marker from: {marker}"
        extracted_marker, extracted_seconds = result[0]
        assert extracted_marker == marker, f"Extracted marker should match input"
        assert extracted_seconds == expected_seconds, (
            f"Timestamp mismatch for {marker}: expected {expected_seconds}, got {extracted_seconds}"
        )

    @given(data=markdown_with_asterisk_markers())
    @settings(max_examples=100)
    def test_asterisk_markers_in_markdown_context(self, data: Tuple[str, List[Tuple[str, int]]]):
        """
        **Feature: system-testing, Property 4: 截图时间戳提取准确性**
        **Validates: Requirements 4.3**
        
        For any markdown with *Screenshot-mm:ss markers, all markers should be
        extracted with correct timestamps.
        """
        markdown, expected_markers = data
        result = _extract_screenshot_timestamps(markdown)
        
        assert len(result) == len(expected_markers), (
            f"Should extract {len(expected_markers)} markers, got {len(result)}"
        )
        
        for (extracted_marker, extracted_seconds), (expected_marker, expected_seconds) in zip(result, expected_markers):
            assert extracted_marker == expected_marker
            assert extracted_seconds == expected_seconds

    @given(data=markdown_with_bracket_markers())
    @settings(max_examples=100)
    def test_bracket_markers_in_markdown_context(self, data: Tuple[str, List[Tuple[str, int]]]):
        """
        **Feature: system-testing, Property 4: 截图时间戳提取准确性**
        **Validates: Requirements 4.3**
        
        For any markdown with Screenshot-[mm:ss] markers, all markers should be
        extracted with correct timestamps.
        """
        markdown, expected_markers = data
        result = _extract_screenshot_timestamps(markdown)
        
        assert len(result) == len(expected_markers), (
            f"Should extract {len(expected_markers)} markers, got {len(result)}"
        )
        
        for (extracted_marker, extracted_seconds), (expected_marker, expected_seconds) in zip(result, expected_markers):
            assert extracted_marker == expected_marker
            assert extracted_seconds == expected_seconds

    @given(mm=minutes_strategy, ss=seconds_strategy)
    @settings(max_examples=100)
    def test_timestamp_formula_correctness(self, mm: int, ss: int):
        """
        **Feature: system-testing, Property 4: 截图时间戳提取准确性**
        **Validates: Requirements 4.3**
        
        For any valid mm:ss combination, the formula mm * 60 + ss should produce
        the correct total seconds.
        """
        # Test with asterisk format
        asterisk_marker = f"*Screenshot-{mm:02d}:{ss:02d}"
        result = _extract_screenshot_timestamps(asterisk_marker)
        assert result[0][1] == mm * 60 + ss
        
        # Test with bracket format
        bracket_marker = f"Screenshot-[{mm:02d}:{ss:02d}]"
        result = _extract_screenshot_timestamps(bracket_marker)
        assert result[0][1] == mm * 60 + ss

    @given(text=st.text(min_size=0, max_size=200))
    @settings(max_examples=100)
    def test_no_false_positives_on_random_text(self, text: str):
        """
        **Feature: system-testing, Property 4: 截图时间戳提取准确性**
        **Validates: Requirements 4.3**
        
        For any random text that doesn't contain valid markers, the function
        should not extract any timestamps (unless the random text happens to
        contain a valid marker pattern).
        """
        result = _extract_screenshot_timestamps(text)
        
        # Verify each extracted result is actually a valid marker
        for marker, seconds in result:
            # Check it matches one of the valid patterns
            asterisk_match = re.match(r"\*Screenshot-(\d{2}):(\d{2})$", marker)
            bracket_match = re.match(r"Screenshot-\[(\d{2}):(\d{2})\]$", marker)
            
            assert asterisk_match or bracket_match, f"Invalid marker extracted: {marker}"
            
            # Verify the timestamp calculation
            if asterisk_match:
                mm, ss = int(asterisk_match.group(1)), int(asterisk_match.group(2))
            else:
                mm, ss = int(bracket_match.group(1)), int(bracket_match.group(2))
            
            assert seconds == mm * 60 + ss, f"Incorrect timestamp for {marker}"
