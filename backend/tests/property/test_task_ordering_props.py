"""
BiliNote Task List Ordering Property Tests

Property-based tests for task list time ordering.
**Feature: system-testing, Property 8: 任务列表时间排序**
**Validates: Requirements 10.4**
"""
import os
import sys
import uuid
from datetime import datetime, timedelta
from hypothesis import given, settings, strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.engine import Base
from app.db.models.video_tasks import VideoTask


# Strategy for generating valid video IDs (ASCII only for simplicity)
video_id_strategy = st.text(
    alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
    min_size=5,
    max_size=15
)

# Strategy for generating platform names
platform_strategy = st.sampled_from(['bilibili', 'youtube', 'douyin', 'kuaishou'])


# Create a single in-memory database for all tests (faster)
_test_engine = None
_test_session_factory = None


def get_test_session():
    """Get a test database session, creating the engine if needed."""
    global _test_engine, _test_session_factory
    
    if _test_engine is None:
        _test_engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            echo=False
        )
        Base.metadata.create_all(bind=_test_engine)
        _test_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)
    
    return _test_session_factory()



class TestTaskListOrdering:
    """
    Property tests for task list time ordering.
    
    **Feature: system-testing, Property 8: 任务列表时间排序**
    **Validates: Requirements 10.4**
    """
    
    @given(
        video_id=video_id_strategy,
        platform=platform_strategy,
        num_tasks=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_tasks_ordered_by_creation_time_desc(self, video_id, platform, num_tasks):
        """
        Property: For any sequence of tasks inserted for the same video,
        querying with order_by(created_at.desc()) should return them
        with timestamps in non-increasing order.
        
        **Feature: system-testing, Property 8: 任务列表时间排序**
        **Validates: Requirements 10.4**
        """
        session = get_test_session()
        
        try:
            # Use unique video_id to avoid conflicts between test runs
            unique_video_id = f"{video_id}_{uuid.uuid4().hex[:8]}"
            
            # Insert multiple tasks with explicit different timestamps
            base_time = datetime.now()
            inserted_task_ids = []
            
            for i in range(num_tasks):
                task_id = f"task-{uuid.uuid4()}"
                task = VideoTask(
                    video_id=unique_video_id,
                    platform=platform,
                    task_id=task_id
                )
                # Manually set created_at with increasing time to ensure ordering
                task.created_at = base_time + timedelta(seconds=i)
                session.add(task)
                session.commit()
                inserted_task_ids.append(task_id)
            
            # Query tasks ordered by created_at descending
            tasks = (
                session.query(VideoTask)
                .filter_by(video_id=unique_video_id, platform=platform)
                .order_by(VideoTask.created_at.desc())
                .all()
            )
            
            # Verify we got all tasks
            assert len(tasks) == num_tasks, f"Expected {num_tasks} tasks, got {len(tasks)}"
            
            # Verify ordering: most recent task should be first
            # The last inserted task (with highest timestamp) should be first
            assert tasks[0].task_id == inserted_task_ids[-1], \
                "Most recently created task should be first"
            
            # Verify all timestamps are in descending order
            for i in range(len(tasks) - 1):
                assert tasks[i].created_at >= tasks[i + 1].created_at, \
                    f"Tasks should be ordered by created_at descending: " \
                    f"{tasks[i].created_at} should be >= {tasks[i + 1].created_at}"
        finally:
            # Clean up tasks created in this test
            session.query(VideoTask).filter(
                VideoTask.video_id == unique_video_id
            ).delete()
            session.commit()
            session.close()
    
    @given(
        video_id=video_id_strategy,
        platform=platform_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_get_latest_task_returns_most_recent(self, video_id, platform):
        """
        Property: For any video with multiple tasks with different timestamps,
        getting the first task with descending order should return the one
        with the most recent timestamp.
        
        **Feature: system-testing, Property 8: 任务列表时间排序**
        **Validates: Requirements 10.4**
        """
        session = get_test_session()
        
        try:
            # Use unique video_id to avoid conflicts between test runs
            unique_video_id = f"{video_id}_{uuid.uuid4().hex[:8]}"
            base_time = datetime.now()
            
            # Insert first task with earlier timestamp
            first_task_id = f"first-{uuid.uuid4()}"
            first_task = VideoTask(
                video_id=unique_video_id,
                platform=platform,
                task_id=first_task_id
            )
            first_task.created_at = base_time
            session.add(first_task)
            session.commit()
            
            # Insert second task with later timestamp
            second_task_id = f"second-{uuid.uuid4()}"
            second_task = VideoTask(
                video_id=unique_video_id,
                platform=platform,
                task_id=second_task_id
            )
            second_task.created_at = base_time + timedelta(seconds=10)
            session.add(second_task)
            session.commit()
            
            # Query for the latest task (same pattern as get_task_by_video)
            latest_task = (
                session.query(VideoTask)
                .filter_by(video_id=unique_video_id, platform=platform)
                .order_by(VideoTask.created_at.desc())
                .first()
            )
            
            # The latest task should be the second one (with later timestamp)
            assert latest_task is not None, "Should find a task"
            assert latest_task.task_id == second_task_id, \
                f"Latest task should be the one with most recent timestamp. " \
                f"Expected: {second_task_id}, Got: {latest_task.task_id}"
        finally:
            # Clean up tasks created in this test
            session.query(VideoTask).filter(
                VideoTask.video_id == unique_video_id
            ).delete()
            session.commit()
            session.close()
