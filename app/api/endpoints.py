from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, Form, File, Response
from fastapi.responses import FileResponse
from typing import Dict, Any, Optional, List, Annotated
import os
import tempfile
import shutil
from pathlib import Path
import uuid
import asyncio

from app.models import (
    TaskStatus, 
    TaskResponse, 
    TaskResult,
)
from app.storage import get_storage
from app.storage.base import StorageInterface
from app.tasks import get_task_runner
from app.core.config import settings
from app.core.logging import get_logger


# Set up logger
logger = get_logger("api")

router = APIRouter()

# Dependency to get storage
def get_task_storage() -> StorageInterface:
    """Get the appropriate storage backend based on configuration"""
    storage_type = settings.STORAGE_TYPE
    logger.debug(f"Using {storage_type} storage backend")
    return get_storage(storage_type)


@router.post("/tasks/chunking_task", response_model=TaskResponse)
async def create_chunking_task(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    strategy: str = Form(...),
    storage: StorageInterface = Depends(get_task_storage)
):
    """
    Start a new chunking task
    
    Takes multiple files and processes them using appropriate parsers based on file type.
    Returns a task ID that can be used to check the status and results.
    """
    task_type = "chunking_task"
    logger.info(f"Creating new {task_type} for {len(files)} files")
    
    # Create base directory if it doesn't exist
    base_dir = Path("/tmp/ai_chunking")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a unique directory for this task
    task_id = str(uuid.uuid4())
    task_dir = base_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    try:
        # Save uploaded files to task directory
        for file in files:
            file_path = task_dir / file.filename
            try:
                # Save uploaded file content
                with open(file_path, "wb") as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    await file.seek(0)  # Reset file pointer for potential reuse
                saved_files.append(str(file_path))
                logger.debug(f"Saved file {file.filename} to {file_path}")
            except Exception as e:
                logger.error(f"Error saving file {file.filename}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}")
        
        # Create a new task result object
        task_result = TaskResult.create_new(task_type=task_type, task_id=task_id)
        logger.debug(f"Generated task ID: {task_id}")

        # Save initial metadata about files
        task_result.result = {
            "input_files": [{"filename": f.filename, "size": len(await f.read())} for f in files],
            "task_dir": str(task_dir),
            "saved_files": saved_files,
            "strategy": strategy
        }
        
        # Save the initial task state
        logger.debug(f"Saving initial task state for {task_id}")
        await storage.save_task(task_result)
        
        # Get the task runner
        task_runner = get_task_runner(task_type, storage)
        logger.debug(f"Created task runner for {task_id}")
        
        # Add task to background tasks
        logger.debug(f"Adding task {task_id} to background tasks")
        print("Strategy: ", strategy)
        background_tasks.add_task(
            task_runner.run_task,
            task_result,
            files=saved_files,
            strategy=strategy
        )
        
        logger.info(f"Successfully initiated task {task_id}")
        
        # Return the task response with ID
        return TaskResponse(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=task_result.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating chunking task: {str(e)}")
        # Clean up task directory in case of error
        shutil.rmtree(task_dir, ignore_errors=True)
        raise


@router.get("/results/{task_id}", response_model=TaskResult)
async def get_task_result(
    task_id: str,
    storage: StorageInterface = Depends(get_task_storage)
):
    """
    Get the status and results of a task
    
    If the task is complete, returns the task result
    If the task is still running, returns the current status
    """
    logger.info(f"Retrieving results for task {task_id}")
    
    task_result = await storage.get_task(task_id)
    
    if not task_result:
        logger.warning(f"Task {task_id} not found")
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    logger.debug(f"Task {task_id} status: {task_result.status}")
    return task_result


@router.get("/tasks", response_model=Dict[str, TaskResult])
async def list_tasks(storage: StorageInterface = Depends(get_task_storage)):
    """List all tasks and their statuses"""
    logger.info("Listing all tasks")
    
    tasks = await storage.list_tasks()
    logger.debug(f"Found {len(tasks)} tasks")
    return tasks


@router.get("/download")
async def download_file(file_path: str):
    """
    Download a file from the server
    
    The file path must be within the /tmp/ai_chunking directory for security
    """
    logger.info(f"Attempting to download file: {file_path}")
    
    # Convert to Path object for safe path manipulation
    file_path = Path(file_path)
    base_dir = Path("/tmp/ai_chunking")
    
    try:
        # Resolve the absolute paths (this also handles any '..' in the path)
        abs_file_path = file_path.resolve()
        abs_base_dir = base_dir.resolve()
        
        # Security check: ensure the file is within the allowed directory
        if not str(abs_file_path).startswith(str(abs_base_dir)):
            logger.warning(f"Attempted to access file outside allowed directory: {file_path}")
            raise HTTPException(
                status_code=403,
                detail="Access to files outside the allowed directory is forbidden"
            )
        
        # Check if file exists
        if not abs_file_path.is_file():
            logger.warning(f"File not found: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get the filename for the download
        filename = abs_file_path.name
        
        logger.info(f"Serving file: {filename}")
        return FileResponse(
            path=str(abs_file_path),
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {file_path}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading file") 