from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskResponse(BaseModel):
    task_id: str
    task_type: str
    status: TaskStatus
    created_at: datetime 


class TaskResult(BaseModel):
    """Model for task result data"""
    task_id: str
    task_type: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    @classmethod
    def create_new(cls, task_type: str, task_id: str = None):
        """Create a new task result with PENDING status"""
        if task_id is None:
            task_id = str(uuid.uuid4())
        return cls(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        ) 