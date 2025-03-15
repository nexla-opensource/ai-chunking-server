"""
FastAPI application main module.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.models import TaskStatus, TaskResponse, TaskResult
from app.storage import get_storage
from app.storage.base import StorageInterface
from app.core.config import Settings, get_settings
from app.api.endpoints import router

# Create FastAPI application
app = FastAPI(
    title="Background Tasks API",
    description="API for running background tasks asynchronously",
    version="1.0.0",
)

# Get settings instance
settings = get_settings()

# Add CORS middleware with simple configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(router, prefix="/api/v1")

@app.get("/", tags=["Health"])
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Root endpoint for health checks
    """
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
    } 