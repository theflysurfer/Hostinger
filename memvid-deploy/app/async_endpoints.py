"""
Async endpoints for MemVid RAG API
To be integrated into api_v2.py
"""

# Add these imports to api_v2.py:
# from .queue import enqueue_indexing, enqueue_chat, get_job_status
# from .jobs import index_text_job, index_folder_job, chat_job

# ===========================================================================
# ASYNC JOB ENDPOINTS
# ===========================================================================

@app.post("/projects/{project_id}/index/text/async")
async def index_text_async(project_id: str, request: IndexTextRequest):
    """
    Index text asynchronously (returns job ID immediately)

    Use this for large texts that may take time to process.
    Check job status with GET /jobs/{job_id}
    """
    try:
        from .queue import enqueue_indexing
        from .jobs import index_text_job

        # Verify project exists
        project = project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Enqueue job
        job = enqueue_indexing(
            index_text_job,
            project_id=project_id,
            text=request.text,
            metadata=request.metadata
        )

        logger.info(f"Enqueued text indexing job {job.id} for project {project_id}")

        return {
            "job_id": job.id,
            "status": "queued",
            "project_id": project_id,
            "message": "Text indexing job queued. Check /jobs/{job_id} for status"
        }

    except Exception as e:
        logger.error(f"Failed to enqueue text indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/index/folder/async")
async def index_folder_async(project_id: str, request: IndexFolderRequest):
    """
    Index folder asynchronously (returns job ID immediately)

    Use this for large folders that may take time to process.
    Check job status with GET /jobs/{job_id}
    """
    try:
        from .queue import enqueue_indexing
        from .jobs import index_folder_job

        # Verify project exists
        project = project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Enqueue job
        job = enqueue_indexing(
            index_folder_job,
            project_id=project_id,
            folder_path=request.folder_path,
            recursive=request.recursive,
            file_extensions=request.file_extensions
        )

        logger.info(f"Enqueued folder indexing job {job.id} for project {project_id}")

        return {
            "job_id": job.id,
            "status": "queued",
            "project_id": project_id,
            "folder_path": request.folder_path,
            "message": "Folder indexing job queued. Check /jobs/{job_id} for status"
        }

    except Exception as e:
        logger.error(f"Failed to enqueue folder indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/chat/async")
async def chat_async(project_id: str, request: ChatRequest):
    """
    RAG chat asynchronously (returns job ID immediately)

    Use this for complex queries that may take time with large models.
    Check job status with GET /jobs/{job_id}
    """
    try:
        from .queue import enqueue_chat
        from .jobs import chat_job

        # Verify project exists
        project = project_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Prepare kwargs for model
        kwargs = {
            "ollama_model": request.ollama_model,
            "ollama_base_url": request.ollama_base_url
        }

        if request.model == "openai":
            kwargs.update({
                "openai_api_key": request.openai_api_key,
                "openai_model": request.openai_model,
                "openai_base_url": request.openai_base_url
            })

        # Enqueue job
        job = enqueue_chat(
            chat_job,
            project_id=project_id,
            query=request.query,
            top_k=request.top_k,
            model=request.model,
            **kwargs
        )

        logger.info(f"Enqueued chat job {job.id} for project {project_id}")

        return {
            "job_id": job.id,
            "status": "queued",
            "project_id": project_id,
            "query": request.query[:100],
            "message": "Chat job queued. Check /jobs/{job_id} for status"
        }

    except Exception as e:
        logger.error(f"Failed to enqueue chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """
    Get job status and result

    Status can be: queued, started, finished, failed, not_found
    """
    try:
        from .queue import get_job_status

        status = get_job_status(job_id)
        return status

    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs")
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List recent jobs

    Args:
        status: Filter by status (queued, started, finished, failed)
        limit: Maximum number of jobs to return
    """
    try:
        from rq.registry import (
            StartedJobRegistry,
            FinishedJobRegistry,
            FailedJobRegistry,
            ScheduledJobRegistry
        )
        from .queue import redis_conn, indexing_queue, chat_queue, default_queue

        jobs = []
        queues = [indexing_queue, chat_queue, default_queue]

        for queue in queues:
            # Get jobs from different registries
            if not status or status == "started":
                started = StartedJobRegistry(queue=queue, connection=redis_conn)
                for job_id in started.get_job_ids()[:limit]:
                    from rq.job import Job
                    job = Job.fetch(job_id, connection=redis_conn)
                    jobs.append({
                        "id": job.id,
                        "queue": queue.name,
                        "status": "started",
                        "created_at": job.created_at.isoformat() if job.created_at else None
                    })

            if not status or status == "finished":
                finished = FinishedJobRegistry(queue=queue, connection=redis_conn)
                for job_id in finished.get_job_ids()[:limit]:
                    from rq.job import Job
                    job = Job.fetch(job_id, connection=redis_conn)
                    jobs.append({
                        "id": job.id,
                        "queue": queue.name,
                        "status": "finished",
                        "created_at": job.created_at.isoformat() if job.created_at else None,
                        "ended_at": job.ended_at.isoformat() if job.ended_at else None
                    })

            if not status or status == "failed":
                failed = FailedJobRegistry(queue=queue, connection=redis_conn)
                for job_id in failed.get_job_ids()[:limit]:
                    from rq.job import Job
                    job = Job.fetch(job_id, connection=redis_conn)
                    jobs.append({
                        "id": job.id,
                        "queue": queue.name,
                        "status": "failed",
                        "created_at": job.created_at.isoformat() if job.created_at else None,
                        "error": job.exc_info
                    })

        return {
            "jobs": jobs[:limit],
            "total": len(jobs)
        }

    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
