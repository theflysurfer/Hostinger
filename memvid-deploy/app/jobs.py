"""
RQ Jobs for MemVid RAG API - Asynchronous task processing
"""
from pathlib import Path
from typing import Dict, Any, List
import time
from loguru import logger
from memvid import MemvidEncoder
from .project_manager import ProjectManager
from .metrics import (
    indexing_operations_total,
    indexing_chunks_total,
    indexing_duration_seconds,
    chat_operations_total,
    chat_duration_seconds,
    chat_context_chunks,
    errors_total
)


def index_text_job(project_id: str, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Async job to index text in a project

    Args:
        project_id: Project ID
        text: Text to index
        metadata: Optional metadata

    Returns:
        Job result with chunks added and total chunks
    """
    start_time = time.time()
    metadata = metadata or {}

    try:
        logger.info(f"[JOB] Starting text indexing for project {project_id}")

        # Load project
        base_dir = Path("/app/data")
        pm = ProjectManager(base_dir)
        project = pm.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Paths
        data_dir = base_dir / "projects" / project_id
        video_path = data_dir / "memory.mp4"
        index_path = data_dir / "memory_index.json"

        # Load existing encoder if exists
        encoder = MemvidEncoder()
        existing_chunks = 0

        if video_path.exists() and index_path.exists():
            try:
                existing_chunks = project.total_chunks
                logger.info(f"Found existing index with {existing_chunks} chunks")
            except Exception as e:
                logger.warning(f"Could not load existing index: {e}")

        # Add new text
        encoder.add_text(text, chunk_size=project.config.chunk_size, overlap=project.config.chunk_overlap)
        new_chunks = len(encoder.chunks)

        # Save
        encoder.build_video(str(video_path), str(index_path))

        # Update project stats
        total_chunks = existing_chunks + new_chunks
        video_size_mb = video_path.stat().st_size / (1024 * 1024) if video_path.exists() else 0

        project.total_chunks = total_chunks
        project.video_size_mb = video_size_mb
        pm.update_project(project_id, project)

        # Update metrics
        duration = time.time() - start_time
        indexing_operations_total.labels(
            project_id=project_id,
            operation_type="text",
            status="success"
        ).inc()
        indexing_chunks_total.labels(project_id=project_id).inc(new_chunks)
        indexing_duration_seconds.labels(operation_type="text").observe(duration)

        logger.info(f"[JOB] Text indexing completed: {new_chunks} new chunks, {total_chunks} total")

        return {
            "success": True,
            "project_id": project_id,
            "chunks_added": new_chunks,
            "total_chunks": total_chunks,
            "video_size_mb": round(video_size_mb, 2),
            "duration_seconds": round(duration, 2)
        }

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[JOB] Text indexing failed: {e}")

        indexing_operations_total.labels(
            project_id=project_id,
            operation_type="text",
            status="error"
        ).inc()
        indexing_duration_seconds.labels(operation_type="text").observe(duration)
        errors_total.labels(endpoint="job_index_text", error_type=type(e).__name__).inc()

        raise


def index_folder_job(
    project_id: str,
    folder_path: str,
    recursive: bool = True,
    file_extensions: List[str] = None
) -> Dict[str, Any]:
    """
    Async job to index a folder in a project

    Args:
        project_id: Project ID
        folder_path: Path to folder
        recursive: Scan recursively
        file_extensions: File extensions to index

    Returns:
        Job result with files indexed and chunks added
    """
    start_time = time.time()
    file_extensions = file_extensions or [".txt", ".md", ".pdf"]

    try:
        logger.info(f"[JOB] Starting folder indexing for project {project_id}: {folder_path}")

        # Load project
        base_dir = Path("/app/data")
        pm = ProjectManager(base_dir)
        project = pm.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Paths
        data_dir = base_dir / "projects" / project_id
        video_path = data_dir / "memory.mp4"
        index_path = data_dir / "memory_index.json"

        # Find files
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")

        files = []
        if recursive:
            for ext in file_extensions:
                files.extend(folder.rglob(f"*{ext}"))
        else:
            for ext in file_extensions:
                files.extend(folder.glob(f"*{ext}"))

        if not files:
            logger.warning(f"No files found in {folder_path}")
            return {
                "success": True,
                "project_id": project_id,
                "files_indexed": 0,
                "chunks_added": 0,
                "total_chunks": project.total_chunks
            }

        # Load existing encoder
        encoder = MemvidEncoder()
        existing_chunks = 0

        if video_path.exists() and index_path.exists():
            try:
                existing_chunks = project.total_chunks
                logger.info(f"Found existing index with {existing_chunks} chunks")
            except Exception as e:
                logger.warning(f"Could not load existing index: {e}")

        # Index files
        files_indexed = 0
        for file_path in files:
            try:
                logger.info(f"Indexing file: {file_path}")

                if file_path.suffix == ".pdf":
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text()
                else:
                    text = file_path.read_text(encoding='utf-8')

                encoder.add_text(
                    text,
                    chunk_size=project.config.chunk_size,
                    overlap=project.config.chunk_overlap
                )
                files_indexed += 1

            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")
                continue

        new_chunks = len(encoder.chunks)

        # Save
        encoder.build_video(str(video_path), str(index_path))

        # Update project stats
        total_chunks = existing_chunks + new_chunks
        video_size_mb = video_path.stat().st_size / (1024 * 1024) if video_path.exists() else 0

        project.total_chunks = total_chunks
        project.video_size_mb = video_size_mb
        project.files_count += files_indexed
        pm.update_project(project_id, project)

        # Update metrics
        duration = time.time() - start_time
        indexing_operations_total.labels(
            project_id=project_id,
            operation_type="folder",
            status="success"
        ).inc()
        indexing_chunks_total.labels(project_id=project_id).inc(new_chunks)
        indexing_duration_seconds.labels(operation_type="folder").observe(duration)

        logger.info(f"[JOB] Folder indexing completed: {files_indexed} files, {new_chunks} chunks")

        return {
            "success": True,
            "project_id": project_id,
            "files_indexed": files_indexed,
            "chunks_added": new_chunks,
            "total_chunks": total_chunks,
            "video_size_mb": round(video_size_mb, 2),
            "duration_seconds": round(duration, 2)
        }

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[JOB] Folder indexing failed: {e}")

        indexing_operations_total.labels(
            project_id=project_id,
            operation_type="folder",
            status="error"
        ).inc()
        indexing_duration_seconds.labels(operation_type="folder").observe(duration)
        errors_total.labels(endpoint="job_index_folder", error_type=type(e).__name__).inc()

        raise


def chat_job(
    project_id: str,
    query: str,
    top_k: int = 3,
    model: str = "ollama",
    **kwargs
) -> Dict[str, Any]:
    """
    Async job for RAG chat

    Args:
        project_id: Project ID
        query: User query
        top_k: Number of chunks to retrieve
        model: LLM model (ollama or openai)
        **kwargs: Additional model parameters

    Returns:
        Chat response with answer and sources
    """
    start_time = time.time()

    try:
        logger.info(f"[JOB] Starting chat for project {project_id}: {query[:50]}...")

        from .api_v2 import perform_chat_internal

        result = perform_chat_internal(
            project_id=project_id,
            query=query,
            top_k=top_k,
            model=model,
            **kwargs
        )

        # Update metrics
        duration = time.time() - start_time
        chat_operations_total.labels(
            project_id=project_id,
            model=model,
            status="success"
        ).inc()
        chat_duration_seconds.labels(model=model).observe(duration)
        chat_context_chunks.observe(result.get("context_chunks", 0))

        logger.info(f"[JOB] Chat completed in {duration:.2f}s")

        return {
            **result,
            "duration_seconds": round(duration, 2)
        }

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"[JOB] Chat failed: {e}")

        chat_operations_total.labels(
            project_id=project_id,
            model=model,
            status="error"
        ).inc()
        chat_duration_seconds.labels(model=model).observe(duration)
        errors_total.labels(endpoint="job_chat", error_type=type(e).__name__).inc()

        raise
