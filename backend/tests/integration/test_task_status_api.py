"""
Integration tests for Task Status API endpoints.

Tests the /api/task_status/{task_id} endpoint.
Requirements: 6.2, 6.3, 6.4
"""
import pytest
import os
import json
import tempfile
from unittest.mock import patch


class TestTaskStatusAPI:
    """Tests for Task Status API endpoints."""

    def test_task_status_pending_for_unknown_task(self, client):
        """
        Test that /api/task_status returns PENDING for unknown task.
        
        Requirements: 6.2 - Should return current status (PENDING for new tasks)
        """
        response = client.get("/api/task_status/unknown-task-id-12345")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "PENDING"
        assert data["data"]["task_id"] == "unknown-task-id-12345"

    def test_task_status_response_format(self, client):
        """
        Test that /api/task_status returns proper response format.
        
        Requirements: 6.2 - Response should include status information
        """
        response = client.get("/api/task_status/test-task-format")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify standard response structure
        assert "code" in data
        assert "msg" in data
        assert "data" in data
        
        # Verify task status data structure
        assert "status" in data["data"]
        assert "task_id" in data["data"]

    def test_task_status_success_with_result_file(self, client):
        """
        Test that /api/task_status returns SUCCESS when result file exists.
        
        Requirements: 6.3 - Should return SUCCESS status when task completes
        """
        task_id = "test-success-task-001"
        note_output_dir = os.getenv("NOTE_OUTPUT_DIR", "note_results")
        
        # Create the output directory if it doesn't exist
        os.makedirs(note_output_dir, exist_ok=True)
        
        # Create a mock result file
        result_file = os.path.join(note_output_dir, f"{task_id}.json")
        mock_result = {
            "markdown": "# Test Note\n\nThis is a test note.",
            "title": "Test Video"
        }
        
        try:
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(mock_result, f)
            
            response = client.get(f"/api/task_status/{task_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["status"] == "SUCCESS"
            assert "result" in data["data"]
            
        finally:
            # Cleanup
            if os.path.exists(result_file):
                os.remove(result_file)

    def test_task_status_failed_with_status_file(self, client):
        """
        Test that /api/task_status returns FAILED when status file indicates failure.
        
        Requirements: 6.4 - Should return FAILED status with error message
        """
        task_id = "test-failed-task-001"
        note_output_dir = os.getenv("NOTE_OUTPUT_DIR", "note_results")
        
        # Create the output directory if it doesn't exist
        os.makedirs(note_output_dir, exist_ok=True)
        
        # Create a mock status file indicating failure
        status_file = os.path.join(note_output_dir, f"{task_id}.status.json")
        mock_status = {
            "status": "FAILED",
            "message": "Test error message"
        }
        
        try:
            with open(status_file, "w", encoding="utf-8") as f:
                json.dump(mock_status, f)
            
            response = client.get(f"/api/task_status/{task_id}")
            
            assert response.status_code == 200
            data = response.json()
            # Failed tasks return error response
            assert data["code"] == 500
            assert "Test error message" in data["msg"]
            
        finally:
            # Cleanup
            if os.path.exists(status_file):
                os.remove(status_file)

    def test_task_status_processing_with_status_file(self, client):
        """
        Test that /api/task_status returns processing status correctly.
        
        Requirements: 6.2 - Should return current status (PROCESSING states)
        """
        task_id = "test-processing-task-001"
        note_output_dir = os.getenv("NOTE_OUTPUT_DIR", "note_results")
        
        # Create the output directory if it doesn't exist
        os.makedirs(note_output_dir, exist_ok=True)
        
        # Create a mock status file indicating processing
        status_file = os.path.join(note_output_dir, f"{task_id}.status.json")
        mock_status = {
            "status": "TRANSCRIBING",
            "message": "正在转录音频"
        }
        
        try:
            with open(status_file, "w", encoding="utf-8") as f:
                json.dump(mock_status, f)
            
            response = client.get(f"/api/task_status/{task_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["status"] == "TRANSCRIBING"
            assert data["data"]["message"] == "正在转录音频"
            
        finally:
            # Cleanup
            if os.path.exists(status_file):
                os.remove(status_file)

    def test_task_status_success_with_both_files(self, client):
        """
        Test that /api/task_status returns result when both status and result files exist.
        
        Requirements: 6.3 - Should return result content on success
        """
        task_id = "test-complete-task-001"
        note_output_dir = os.getenv("NOTE_OUTPUT_DIR", "note_results")
        
        # Create the output directory if it doesn't exist
        os.makedirs(note_output_dir, exist_ok=True)
        
        # Create mock files
        status_file = os.path.join(note_output_dir, f"{task_id}.status.json")
        result_file = os.path.join(note_output_dir, f"{task_id}.json")
        
        mock_status = {
            "status": "SUCCESS",
            "message": "任务完成"
        }
        mock_result = {
            "markdown": "# Complete Note\n\nThis is a complete note.",
            "title": "Complete Video",
            "transcript": "This is the transcript."
        }
        
        try:
            with open(status_file, "w", encoding="utf-8") as f:
                json.dump(mock_status, f)
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(mock_result, f)
            
            response = client.get(f"/api/task_status/{task_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["status"] == "SUCCESS"
            assert "result" in data["data"]
            assert data["data"]["result"]["markdown"] == mock_result["markdown"]
            
        finally:
            # Cleanup
            if os.path.exists(status_file):
                os.remove(status_file)
            if os.path.exists(result_file):
                os.remove(result_file)
