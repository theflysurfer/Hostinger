"""
MemVid RAG API v2 - Multi-project support with Streamlit UI
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import shutil
from pathlib import Path
from loguru import logger
import os

# Configure logging
logger.add(
    "/app/logs/memvid-api.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO"
)

# Import MemVid
try:
    from memvid import MemvidEncoder, MemvidRetriever
    logger.info("MemVid library loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import MemVid: {e}")
    raise

# Import our models and managers
from .models import (
    Project, ProjectCreate, ProjectUpdate, ProjectStats,
    IndexTextRequest, IndexFolderRequest,
    SearchRequest, SearchResult,
    ChatRequest, ChatResponse
)
from .project_manager import ProjectManager

# Initialize FastAPI
app = FastAPI(
    title="MemVid RAG API v2",
    description="Multi-project video-based RAG system with semantic search",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize project manager
DATA_DIR = Path("/app/data")
project_manager = ProjectManager(DATA_DIR)
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "MemVid RAG API v2",
        "version": "2.0.0",
        "status": "running",
        "features": ["multi-project", "semantic-search", "rag-chat", "folder-indexing"]
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        from .metrics import get_metrics
        return get_metrics()
    except ImportError:
        # Fallback if metrics module not available
        return {"error": "Metrics not available"}


@app.post("/projects", response_model=Project)
async def create_project(request: ProjectCreate):
    """Create a new RAG project"""
    try:
        project = project_manager.create_project(request)
        logger.info(f"Created project: {project.name}")
        return project
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects", response_model=List[Project])
async def list_projects():
    """List all projects"""
    return project_manager.list_projects()


@app.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get project by ID"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, request: ProjectUpdate):
    """Update project"""
    project = project_manager.update_project(project_id, request)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete project"""
    success = project_manager.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "message": f"Project {project_id} deleted"}


@app.get("/projects/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(project_id: str):
    """Get project statistics"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectStats(
        id=project.id,
        name=project.name,
        total_chunks=project.total_chunks,
        video_size_mb=project.video_size_mb,
        files_count=project.files_count,
        last_updated=project.updated_at
    )


# ============================================================================
# INDEXING ENDPOINTS
# ============================================================================

@app.post("/projects/{project_id}/index/text")
async def index_text(project_id: str, request: IndexTextRequest):
    """Index raw text in a project (incremental)"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        logger.info(f"Indexing text in project {project.name}: {len(request.text)} chars")

        video_path = project_manager.get_project_video_path(project_id)
        index_path = project_manager.get_project_index_path(project_id)

        # Load existing encoder if it exists, otherwise create new
        encoder = MemvidEncoder()
        existing_chunks = 0

        if video_path.exists() and index_path.exists():
            try:
                # Load existing data to get current chunks count
                retriever = MemvidRetriever(str(video_path), str(index_path))
                # Get existing chunks from the encoder's internal state
                # Note: MemVid doesn't have a direct way to reload chunks,
                # so we track this separately
                existing_chunks = project.total_chunks
                logger.info(f"Found existing index with {existing_chunks} chunks")
            except Exception as e:
                logger.warning(f"Could not load existing index: {e}, will recreate")

        # Add new text
        encoder.add_text(
            request.text,
            chunk_size=project.config.chunk_size,
            overlap=project.config.chunk_overlap
        )

        new_chunks = len(encoder.chunks)
        logger.info(f"Added {new_chunks} new chunks")

        # Build/rebuild video with all chunks
        encoder.build_video(str(video_path), str(index_path))

        # Update project stats with cumulative count
        total_chunks = existing_chunks + new_chunks
        video_size_mb = video_path.stat().st_size / (1024 * 1024)
        project_manager.update_project_stats(
            project_id,
            total_chunks=total_chunks,
            video_size_mb=round(video_size_mb, 2),
            files_count=project.files_count
        )

        logger.info(f"Total: {total_chunks} chunks in project {project.name}")

        return {
            "success": True,
            "project_id": project_id,
            "chunks_added": new_chunks,
            "total_chunks": total_chunks,
            "video_size_mb": round(video_size_mb, 2)
        }

    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/index/upload")
async def upload_and_index(
    project_id: str,
    file: UploadFile = File(...),
    chunk_size: Optional[int] = None,
    overlap: Optional[int] = None
):
    """Upload and index a file in a project"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    file_path = UPLOAD_DIR / file.filename
    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded: {file.filename} for project {project.name}")

        # Use project config or override
        cs = chunk_size if chunk_size else project.config.chunk_size
        ov = overlap if overlap else project.config.chunk_overlap

        encoder = MemvidEncoder()

        file_ext = file_path.suffix.lower()

        if file_ext == ".pdf":
            encoder.add_pdf(str(file_path))
        elif file_ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            encoder.add_text(text, chunk_size=cs, overlap=ov)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported: {file_ext}")

        video_path = project_manager.get_project_video_path(project_id)
        index_path = project_manager.get_project_index_path(project_id)

        encoder.build_video(str(video_path), str(index_path))

        # Copy file to project files directory
        files_dir = project_manager.get_project_files_dir(project_id)
        dest_path = files_dir / file.filename
        shutil.copy2(file_path, dest_path)

        # Update project stats
        video_size_mb = video_path.stat().st_size / (1024 * 1024)
        files_count = len(list(files_dir.glob("*")))
        project_manager.update_project_stats(
            project_id,
            total_chunks=len(encoder.chunks),
            video_size_mb=round(video_size_mb, 2),
            files_count=files_count
        )

        # Cleanup upload
        file_path.unlink()

        logger.info(f"File indexed: {file.filename}, {len(encoder.chunks)} chunks")

        return {
            "success": True,
            "project_id": project_id,
            "filename": file.filename,
            "chunks_added": len(encoder.chunks),
            "video_size_mb": round(video_size_mb, 2)
        }

    except Exception as e:
        logger.error(f"Upload indexing error: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/index/folder")
async def index_folder(project_id: str, request: IndexFolderRequest):
    """Index all files in a folder"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    folder_path = Path(request.folder_path)
    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(status_code=400, detail="Invalid folder path")

    try:
        logger.info(f"Indexing folder {request.folder_path} for project {project.name}")

        cs = request.chunk_size if request.chunk_size else project.config.chunk_size
        ov = request.chunk_overlap if request.chunk_overlap else project.config.chunk_overlap

        encoder = MemvidEncoder()
        files_indexed = []

        # Collect files
        for ext in request.file_extensions:
            if request.recursive:
                files = folder_path.rglob(f"*{ext}")
            else:
                files = folder_path.glob(f"*{ext}")

            for file_path in files:
                if not file_path.is_file():
                    continue

                try:
                    if ext == ".pdf":
                        encoder.add_pdf(str(file_path))
                    elif ext in [".txt", ".md"]:
                        with open(file_path, "r", encoding="utf-8") as f:
                            text = f.read()
                        encoder.add_text(text, chunk_size=cs, overlap=ov)

                    files_indexed.append(file_path.name)
                    logger.info(f"Indexed file: {file_path.name}")

                except Exception as e:
                    logger.warning(f"Failed to index {file_path.name}: {e}")

        if len(files_indexed) == 0:
            raise HTTPException(status_code=400, detail="No files found to index")

        video_path = project_manager.get_project_video_path(project_id)
        index_path = project_manager.get_project_index_path(project_id)

        encoder.build_video(str(video_path), str(index_path))

        # Update project stats
        video_size_mb = video_path.stat().st_size / (1024 * 1024)
        files_dir = project_manager.get_project_files_dir(project_id)
        files_count = len(list(files_dir.glob("*")))

        project_manager.update_project_stats(
            project_id,
            total_chunks=len(encoder.chunks),
            video_size_mb=round(video_size_mb, 2),
            files_count=files_count + len(files_indexed)
        )

        logger.info(f"Indexed {len(files_indexed)} files, {len(encoder.chunks)} chunks")

        return {
            "success": True,
            "project_id": project_id,
            "files_indexed": files_indexed,
            "chunks_added": len(encoder.chunks),
            "video_size_mb": round(video_size_mb, 2)
        }

    except Exception as e:
        logger.error(f"Folder indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SEARCH AND CHAT ENDPOINTS
# ============================================================================

@app.post("/projects/{project_id}/search", response_model=List[SearchResult])
async def search(project_id: str, request: SearchRequest):
    """Semantic search in a project"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    video_path = project_manager.get_project_video_path(project_id)
    index_path = project_manager.get_project_index_path(project_id)

    if not video_path.exists() or not index_path.exists():
        raise HTTPException(status_code=400, detail="Project not indexed yet")

    try:
        logger.info(f"Search in project {project.name}: {request.query}")

        retriever = MemvidRetriever(str(video_path), str(index_path))
        results = retriever.search(request.query, top_k=request.top_k)

        formatted = [
            SearchResult(
                text=r if isinstance(r, str) else str(r),
                score=1.0,
                metadata={}
            )
            for r in results
        ]

        logger.info(f"Found {len(formatted)} results")
        return formatted

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/projects/{project_id}/chat", response_model=ChatResponse)
async def chat(project_id: str, request: ChatRequest):
    """Chat with RAG context from a project"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    video_path = project_manager.get_project_video_path(project_id)
    index_path = project_manager.get_project_index_path(project_id)

    if not video_path.exists() or not index_path.exists():
        raise HTTPException(status_code=400, detail="Project not indexed yet")

    try:
        logger.info(f"Chat in project {project.name}: {request.query}")

        retriever = MemvidRetriever(str(video_path), str(index_path))
        results = retriever.search(request.query, top_k=request.top_k)

        context = "\n\n".join([r if isinstance(r, str) else str(r) for r in results])

        prompt = f"""Context:
{context}

Question: {request.query}

Answer based on the context above:"""

        if request.model == "ollama":
            import httpx

            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{request.ollama_base_url}/api/generate",
                    json={
                        "model": request.ollama_model,
                        "prompt": prompt,
                        "stream": False
                    }
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Ollama error: {response.text}"
                    )

                ollama_response = response.json()
                answer = ollama_response.get("response", "")

                if not answer:
                    logger.warning(f"Empty response from Ollama: {ollama_response}")
                    answer = "No answer generated. Please try again."

        elif request.model == "openai":
            import httpx

            if not request.openai_api_key:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key required for openai model"
                )

            base_url = request.openai_base_url or "https://api.openai.com/v1"

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {request.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": request.openai_model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"OpenAI error: {response.text}"
                    )

                openai_response = response.json()
                answer = openai_response.get("choices", [{}])[0].get("message", {}).get("content", "")

                if not answer:
                    logger.warning(f"Empty response from OpenAI: {openai_response}")
                    answer = "No answer generated. Please try again."

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model: {request.model}. Use 'ollama' or 'openai'"
            )

        logger.info("Chat completed")

        return ChatResponse(
            answer=answer,
            context_chunks=len(results),
            sources=[
                {
                    "text": (r if isinstance(r, str) else str(r))[:200] + "...",
                    "score": 1.0
                }
                for r in results
            ]
        )

    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"Chat error: {error_msg}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg if error_msg else "Unknown error occurred")


@app.delete("/projects/{project_id}/reset")
async def reset_project_memory(project_id: str):
    """Reset project memory (delete indexed data)"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        video_path = project_manager.get_project_video_path(project_id)
        index_path = project_manager.get_project_index_path(project_id)

        if video_path.exists():
            video_path.unlink()
        if index_path.exists():
            index_path.unlink()

        # Update project stats
        project_manager.update_project_stats(
            project_id,
            total_chunks=0,
            video_size_mb=0.0,
            files_count=0
        )

        logger.info(f"Reset memory for project {project.name}")

        return {"success": True, "message": f"Project {project_id} memory reset"}

    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8503)
