"""
RQ Queue configuration for MemVid RAG API
"""
import os
from redis import Redis
from rq import Queue
from loguru import logger

# Redis configuration from environment
REDIS_HOST = os.getenv("REDIS_HOST", "whisperx-redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "1"))  # Use DB 1 for MemVid (WhisperX uses DB 0)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Initialize Redis connection
redis_conn = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=False
)

# Create queues with different priorities
default_queue = Queue("memvid-default", connection=redis_conn, default_timeout=600)  # 10 minutes
indexing_queue = Queue("memvid-indexing", connection=redis_conn, default_timeout=3600)  # 1 hour
chat_queue = Queue("memvid-chat", connection=redis_conn, default_timeout=300)  # 5 minutes

logger.info(f"RQ configured: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")


def get_job_status(job_id: str) -> dict:
    """
    Get job status from RQ

    Args:
        job_id: Job ID

    Returns:
        Job status dict
    """
    from rq.job import Job

    try:
        job = Job.fetch(job_id, connection=redis_conn)

        return {
            "id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "result": job.result if job.is_finished else None,
            "exc_info": job.exc_info if job.is_failed else None,
            "meta": job.meta
        }

    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        return {
            "id": job_id,
            "status": "not_found",
            "error": str(e)
        }


def enqueue_indexing(func, *args, **kwargs):
    """Enqueue an indexing job"""
    job = indexing_queue.enqueue(func, *args, **kwargs)
    logger.info(f"Enqueued indexing job: {job.id}")
    return job


def enqueue_chat(func, *args, **kwargs):
    """Enqueue a chat job"""
    job = chat_queue.enqueue(func, *args, **kwargs)
    logger.info(f"Enqueued chat job: {job.id}")
    return job
