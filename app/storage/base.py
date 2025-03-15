from abc import ABC, abstractmethod
from typing import Dict, Optional
from app.models import TaskResult


class StorageInterface(ABC):
    """Abstract base class for task storage implementations"""
    
    @abstractmethod
    async def save_task(self, task: TaskResult) -> None:
        """Save a task result"""
        pass
    
    @abstractmethod
    async def get_task(self, task_id: str) -> Optional[TaskResult]:
        """Get a task result by ID"""
        pass
    
    @abstractmethod
    async def list_tasks(self) -> Dict[str, TaskResult]:
        """List all tasks"""
        pass 