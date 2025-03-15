# FastAPI Background Tasks Server

A FastAPI server that runs asynchronous background tasks and provides endpoints to check task status and results.

## Features

- Run multiple types of background tasks asynchronously
- Get a reference ID for each task
- Check task status and results using the reference ID
- Store task data in Redis or file system

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure storage:
   - Create a `.env` file with the following variables:
   ```
   STORAGE_TYPE=file  # or 'redis'
   REDIS_URL=redis://localhost:6379/0  # only needed if using Redis
   FILE_STORAGE_PATH=./data  # only needed if using file storage
   ```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /tasks/{task_type}`: Start a new background task
- `GET /results/{task_id}`: Get the status and results of a task

## Example

Start a task:
```bash

```

Check results:
```bash
curl http://localhost:8000/results/5f3e7c2a-9b4d-4f1e-8a6c-3d7a8b9c0d1e
``` 