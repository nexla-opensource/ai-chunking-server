import json
import os
import aiofiles
import logging
from typing import Dict, Optional
from datetime import datetime
import aiofiles.os

from app.models import TaskResult
from app.storage.base import StorageInterface


class FileStorage(StorageInterface):
    """Implementation of StorageInterface using the file system"""

    def __init__(self, storage_path: str):
        """Initialize with the path to store task files"""
        super().__init__()
        self.storage_path = storage_path
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing file storage at {storage_path}")
        os.makedirs(storage_path, exist_ok=True)
    
    def _get_file_path(self, task_id: str) -> str:
        """Get the file path for a task ID"""
        return os.path.join(self.storage_path, f"{task_id}.json")
    
    async def save_task(self, task: TaskResult) -> None:
        """Save a task to a JSON file"""
        file_path = self._get_file_path(task.task_id)
        self.logger.debug(f"Saving task {task.task_id} to {file_path}")
        
        # Convert the task to a dict and handle datetime serialization
        task_dict = task.dict()
        for field in ['created_at', 'started_at', 'completed_at']:
            if task_dict.get(field) is not None:
                task_dict[field] = task_dict[field].isoformat()
                
        try:
            async with aiofiles.open(file_path, mode='w') as f:
                await f.write(json.dumps(task_dict, indent=2))
            self.logger.debug(f"Successfully saved task {task.task_id}")
        except Exception as e:
            self.logger.error(f"Error saving task {task.task_id}: {str(e)}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[TaskResult]:
        """Get a task from the file system by ID"""
        file_path = self._get_file_path(task_id)
        self.logger.debug(f"Retrieving task {task_id} from {file_path}")
        
        if not os.path.exists(file_path):
            self.logger.warning(f"Task {task_id} not found at {file_path}")
            return None
            
        try:
            async with aiofiles.open(file_path, mode='r') as f:
                content = await f.read()
                task_dict = json.loads(content)
                
            # Convert ISO datetime strings back to datetime objects
            for field in ['created_at', 'started_at', 'completed_at']:
                if task_dict.get(field) is not None:
                    task_dict[field] = datetime.fromisoformat(task_dict[field])
            
            self.logger.debug(f"Successfully retrieved task {task_id}")
            return TaskResult(**task_dict)
        except Exception as e:
            self.logger.error(f"Error retrieving task {task_id}: {str(e)}")
            return None
    
    async def list_tasks(self) -> Dict[str, TaskResult]:
        """List all tasks in the file system storage"""
        tasks = {}
        self.logger.debug(f"Listing all tasks in {self.storage_path}")
        
        if not os.path.exists(self.storage_path):
            self.logger.warning(f"Storage path {self.storage_path} does not exist")
            return tasks
            
        try:
            task_files = [f for f in os.listdir(self.storage_path) if f.endswith('.json')]
            self.logger.debug(f"Found {len(task_files)} task files")
            
            for filename in task_files:
                task_id = filename[:-5]  # Remove .json extension
                task = await self.get_task(task_id)
                if task:
                    tasks[task_id] = task
            
            return tasks
        except Exception as e:
            self.logger.error(f"Error listing tasks: {str(e)}")
            return {} 