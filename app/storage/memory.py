from typing import Dict, Optional
from copy import deepcopy
from app.models import TaskResult
from app.storage.base import StorageInterface
from app.core.logging import get_logger


class InMemoryStorage(StorageInterface):
    """In-memory implementation of task storage"""
    
    def __init__(self):
        self._tasks: Dict[str, TaskResult] = {}
        self.logger = get_logger("storage.memory")
        self.logger.info("Initialized in-memory storage")
    
    async def save_task(self, task: TaskResult) -> None:
        """Save a task result to memory"""
        self.logger.debug(f"Saving task {task.task_id} (status: {task.status})")
        # Create a deep copy to ensure task state is properly maintained
        self._tasks[task.task_id] = deepcopy(task)
    
    async def get_task(self, task_id: str) -> Optional[TaskResult]:
        """Get a task result from memory by ID"""
        task = self._tasks.get(task_id)
        if task:
            # Return a deep copy to prevent accidental modifications
            return deepcopy(task)
        else:
            self.logger.warning(f"Task {task_id} not found in storage")
            return None
    
    async def list_tasks(self) -> Dict[str, TaskResult]:
        """List all tasks from memory"""
        # Return a deep copy of all tasks
        return {k: deepcopy(v) for k, v in self._tasks.items()} 