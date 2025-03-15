from typing import Optional
import os
from functools import lru_cache

from app.storage.base import StorageInterface
from app.storage.file_storage import FileStorage
from app.storage.redis_storage import RedisStorage
from app.storage.memory import InMemoryStorage

# Global storage instances cache
_storage_instances = {}

@lru_cache()
def get_storage(storage_type: str = "memory") -> StorageInterface:
    """Get the appropriate storage implementation with caching for in-memory storage"""
    storage_type = storage_type.lower()
    
    # Check if we already have an instance for this storage type
    if storage_type in _storage_instances:
        return _storage_instances[storage_type]
    
    # Create a new instance
    if storage_type == "memory":
        _storage_instances[storage_type] = InMemoryStorage()
        return _storage_instances[storage_type]
    elif storage_type == "redis":
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        _storage_instances[storage_type] = RedisStorage(redis_url=redis_url)
        return _storage_instances[storage_type]
    elif storage_type == "file":
        storage_path = os.environ.get("FILE_STORAGE_PATH", "./data")
        _storage_instances[storage_type] = FileStorage(storage_path=storage_path)
        return _storage_instances[storage_type]
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
