import asyncio
from datetime import datetime
from typing import Dict, Any
from abc import ABC, abstractmethod

from app.models import TaskResult, TaskStatus
from app.storage.base import StorageInterface
from app.core.logging import get_logger

logger = get_logger("tasks.base")


class BaseTaskRunner(ABC):
    """Base class for task runners"""
    
    def __init__(self, storage: StorageInterface):
        """Initialize with storage backend"""
        self.storage = storage
        logger.debug(f"Initialized {self.__class__.__name__} task runner")
        self.task_timeout = 3600  # Default to 1 hour timeout
    
    async def run_task(self, task: TaskResult, **kwargs) -> None:
        """Run the task and update its status"""
        try:
            # Store task result as instance variable
            self.task_result = task
            
            # Update status to running
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            await self.storage.save_task(task)
            
            logger.info(f"Starting task {task.task_id} of type {task.task_type}")
            
            # Execute the task
            result = await self._execute(**kwargs)
            
            # Update with success
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result
            await self.storage.save_task(task)
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {str(e)}")
            # Update with failure
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = str(e)
            await self.storage.save_task(task)
            raise
    
    @abstractmethod
    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the actual task logic"""
        pass

    async def _run_implementation(self, **kwargs) -> Dict[str, Any]:
        """
        Implement this method in subclasses to define the actual task functionality.
        Should return a dictionary with the task results.
        """
        raise NotImplementedError("Subclasses must implement _run_implementation") 