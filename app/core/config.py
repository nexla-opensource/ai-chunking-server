import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from functools import lru_cache

# Load environment variables from .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Basic app settings
    APP_NAME: str = "FastAPI Background Tasks Server"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API documentation
    API_TITLE: str = "Background Tasks API"
    API_DESCRIPTION: str = "API for running background tasks asynchronously"
    API_VERSION: str = "1.0.0"
    
    # Storage settings
    STORAGE_TYPE: str = "memory"
    FILE_STORAGE_PATH: str = "./data"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    LOG_FORMAT: str = "[%(asctime)s] %(levelname)-8s %(name)s - %(message)s"
    
    # Security settings
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://localhost:5173"
    SECRET_KEY: str = "supersecretkey"
    AUTH_ENABLED: bool = False
    
    # Task settings
    TASK_TIMEOUT: int = 3600  # 1 hour in seconds
    
    # Override settings from environment variables
    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "extra": "ignore",
        "case_sensitive": True
    }

    @property
    def cors_origin_list(self) -> List[str]:
        """Get list of allowed CORS origins"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

# Create logs directory
os.makedirs(os.environ.get("LOG_DIR", "./logs"), exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Create a module-level settings instance
settings = get_settings() 