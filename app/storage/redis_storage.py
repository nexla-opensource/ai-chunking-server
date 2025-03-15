import json
from typing import Dict, Optional
from datetime import datetime
import redis.asyncio as redis

from app.models import TaskResult
from app.storage.base import StorageInterface


class RedisStorage(StorageInterface):
    """Implementation of StorageInterface using Redis"""

    def __init__(self, redis_url: str):
        """Initialize with Redis connection URL"""
        super().__init__()
        self.redis_url = redis_url
        self.logger.info(f"Initializing Redis storage with URL: {redis_url}")
        self.redis_client = redis.from_url(redis_url)
        self.key_prefix = "task:"
    
    def _get_key(self, task_id: str) -> str:
        """Get the Redis key for a task ID"""
        return f"{self.key_prefix}{task_id}"
    
    async def save_task(self, task: TaskResult) -> None:
        """Save a task to Redis"""
        key = self._get_key(task.task_id)
        self.logger.debug(f"Saving task {task.task_id} to Redis key {key}")
        
        # Convert the task to a dict and handle datetime serialization
        task_dict = task.dict()
        for field in ['created_at', 'started_at', 'completed_at']:
            if task_dict.get(field) is not None:
                task_dict[field] = task_dict[field].isoformat()
        
        try:        
            await self.redis_client.set(key, json.dumps(task_dict))
            self.logger.debug(f"Successfully saved task {task.task_id}")
        except Exception as e:
            self.logger.error(f"Error saving task {task.task_id}: {str(e)}")
            raise
    
    async def get_task(self, task_id: str) -> Optional[TaskResult]:
        """Get a task from Redis by ID"""
        key = self._get_key(task_id)
        self.logger.debug(f"Retrieving task {task_id} from Redis key {key}")
        
        try:
            task_json = await self.redis_client.get(key)
            
            if not task_json:
                self.logger.warning(f"Task {task_id} not found in Redis")
                return None
                
            task_dict = json.loads(task_json)
            
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
        """List all tasks in Redis storage"""
        tasks = {}
        self.logger.debug(f"Listing all tasks with prefix {self.key_prefix}")
        
        try:
            # Get all keys with our prefix
            keys = await self.redis_client.keys(f"{self.key_prefix}*")
            self.logger.debug(f"Found {len(keys)} task keys in Redis")
            
            for key in keys:
                task_id = key.decode('utf-8').replace(self.key_prefix, "")
                task = await self.get_task(task_id)
                if task:
                    tasks[task_id] = task
            
            return tasks
        except Exception as e:
            self.logger.error(f"Error listing tasks: {str(e)}")
            return {} 