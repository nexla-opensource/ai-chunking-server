import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

from app.core.config import settings
from app.core.logging import get_logger


def cleanup_old_logs():
    """
    Clean up log files older than the retention period
    specified in settings.LOG_RETENTION_DAYS
    """
    logger = get_logger("log_cleanup")
    log_dir = Path(settings.LOG_DIR)
    retention_days = 30  # Default to 30 days
    
    if not log_dir.exists():
        logger.warning(f"Log directory {log_dir} does not exist, nothing to clean up")
        return
    
    logger.info(f"Cleaning up log files older than {retention_days} days in {log_dir}")
    
    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    cutoff_timestamp = cutoff_date.timestamp()
    
    # Get all log files
    log_files = [f for f in log_dir.glob("*.log")]
    total_files = len(log_files)
    deleted_files = 0
    
    for log_file in log_files:
        file_mtime = log_file.stat().st_mtime
        if file_mtime < cutoff_timestamp:
            try:
                log_file.unlink()
                deleted_files += 1
                logger.debug(f"Deleted old log file: {log_file}")
            except Exception as e:
                logger.error(f"Failed to delete log file {log_file}: {str(e)}")
    
    logger.info(f"Log cleanup complete. Deleted {deleted_files} of {total_files} files")


if __name__ == "__main__":
    # This allows the script to be run directly for manual cleanup
    cleanup_old_logs() 