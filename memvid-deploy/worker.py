"""
RQ Worker for MemVid RAG API
Processes asynchronous jobs for indexing and chat operations
"""
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from redis import Redis
from rq import Worker, Queue
from loguru import logger

# Configure logging
logger.add(
    "/app/logs/memvid-worker.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO"
)

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "whisperx-redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "1"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

if __name__ == "__main__":
    logger.info(f"Starting RQ worker: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

    # Connect to Redis
    redis_conn = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=False
    )

    # Listen to queues (priority order)
    listen_queues = ["memvid-chat", "memvid-indexing", "memvid-default"]

    # Create worker and start processing
    worker = Worker(listen_queues, connection=redis_conn)
    logger.info(f"Worker listening to queues: {listen_queues}")
    worker.work()
