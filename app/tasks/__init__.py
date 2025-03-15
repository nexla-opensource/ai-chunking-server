from typing import Dict, Type

from app.storage.base import StorageInterface
from app.tasks.base import BaseTaskRunner
from app.tasks.runners import ChunkingTaskRunner

# Map of task type names to task runner classes
TASK_RUNNERS: Dict[str, Type[BaseTaskRunner]] = {
    "chunking_task": ChunkingTaskRunner,
}

def get_task_runner(task_type: str, storage: StorageInterface) -> BaseTaskRunner:
    """Get the appropriate task runner for the given task type"""
    if task_type not in TASK_RUNNERS:
        raise ValueError(f"Unknown task type: {task_type}")
    return TASK_RUNNERS[task_type](storage)
