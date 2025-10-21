"""
MemVid RAG API - FastAPI service for semantic search with video-based memory
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import shutil
from pathlib import Path
import json
from datetime import datetime
from loguru import logger

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

# Initialize FastAPI
app = FastAPI(
    title="MemVid RAG API",
    description="Video-based RAG system with semantic search",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
DATA_DIR = Path("/app/data/memory")
UPLOAD_DIR = Path("/app/data/uploads")

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Global memory state
VIDEO_PATH = DATA_DIR / "memory.mp4"
INDEX_PATH = DATA_DIR / "memory_index.json"
METADATA_PATH = DATA_DIR / "metadata.json"


# Pydantic models
class IndexRequest(BaseModel):
    text: Optional[str] = Field(None, description="Raw text to index")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=50)


class SearchResult(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=20)
    model: str = Field("ollama", description="LLM to use")
    ollama_model: str = Field("qwen2.5:14b")
    ollama_base_url: str = Field("http://host.docker.internal:11434")


class StatusResponse(BaseModel):
    indexed: bool
    total_chunks: int
    video_size_mb: float
    last_updated: Optional[str]
    metadata: Dict[str, Any]


# Helper functions
def load_metadata() -> Dict[str, Any]:
    """Load memory metadata"""
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    return {
        "total_chunks": 0,
        "created_at": None,
        "last_updated": None,
        "sources": []
    }


def save_metadata(metadata: Dict[str, Any]):
    """Save memory metadata"""
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)


def is_indexed() -> bool:
    """Check if memory is indexed"""
    return VIDEO_PATH.exists() and INDEX_PATH.exists()


# API Endpoints
@app.get("/")
async def root():
    return {
        "service": "MemVid RAG API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get memory status"""
    metadata = load_metadata()

    video_size_mb = 0.0
    if VIDEO_PATH.exists():
        video_size_mb = VIDEO_PATH.stat().st_size / (1024 * 1024)

    return StatusResponse(
        indexed=is_indexed(),
        total_chunks=metadata.get("total_chunks", 0),
        video_size_mb=round(video_size_mb, 2),
        last_updated=metadata.get("last_updated"),
        metadata=metadata
    )


@app.post("/index/text")
async def index_text(request: IndexRequest):
    """Index raw text"""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        logger.info(f"Indexing text: {len(request.text)} characters")

        encoder = MemvidEncoder()
        encoder.add_text(request.text, chunk_size=512, overlap=64)
        encoder.build_video(str(VIDEO_PATH), str(INDEX_PATH))

        metadata = load_metadata()
        metadata["total_chunks"] = len(encoder.chunks)
        metadata["last_updated"] = datetime.now().isoformat()
        if not metadata["created_at"]:
            metadata["created_at"] = metadata["last_updated"]
        metadata["sources"].append({
            "type": "text",
            "added_at": metadata["last_updated"],
            "metadata": request.metadata
        })
        save_metadata(metadata)

        logger.info(f"Indexed: {len(encoder.chunks)} chunks")

        return {
            "success": True,
            "chunks_added": len(encoder.chunks),
            "video_size_mb": round(VIDEO_PATH.stat().st_size / (1024 * 1024), 2)
        }

    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index/upload")
async def upload_and_index(
    file: UploadFile = File(...),
    chunk_size: int = 512,
    overlap: int = 64
):
    """Upload and index a file"""
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"File uploaded: {file.filename}")

        encoder = MemvidEncoder()

        file_ext = file_path.suffix.lower()

        if file_ext == ".pdf":
            encoder.add_pdf(str(file_path))
        elif file_ext in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            encoder.add_text(text, chunk_size=chunk_size, overlap=overlap)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported: {file_ext}")

        encoder.build_video(str(VIDEO_PATH), str(INDEX_PATH))

        metadata = load_metadata()
        metadata["total_chunks"] = len(encoder.chunks)
        metadata["last_updated"] = datetime.now().isoformat()
        if not metadata["created_at"]:
            metadata["created_at"] = metadata["last_updated"]
        metadata["sources"].append({
            "type": "file",
            "filename": file.filename,
            "added_at": metadata["last_updated"]
        })
        save_metadata(metadata)

        file_path.unlink()

        logger.info(f"File indexed: {file.filename}, {len(encoder.chunks)} chunks")

        return {
            "success": True,
            "filename": file.filename,
            "chunks_added": len(encoder.chunks),
            "video_size_mb": round(VIDEO_PATH.stat().st_size / (1024 * 1024), 2)
        }

    except Exception as e:
        logger.error(f"Upload error: {e}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest):
    """Semantic search"""
    if not is_indexed():
        raise HTTPException(status_code=400, detail="No memory indexed")

    try:
        logger.info(f"Search: {request.query}")

        retriever = MemvidRetriever(str(VIDEO_PATH), str(INDEX_PATH))
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


@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with RAG"""
    if not is_indexed():
        raise HTTPException(status_code=400, detail="No memory indexed")

    try:
        logger.info(f"Chat: {request.query}")

        retriever = MemvidRetriever(str(VIDEO_PATH), str(INDEX_PATH))
        results = retriever.search(request.query, top_k=request.top_k)

        context = "\n\n".join([r if isinstance(r, str) else str(r) for r in results])

        prompt = f"""Context:
{context}

Question: {request.query}

Answer based on the context above:"""

        if request.model == "ollama":
            import httpx

            async with httpx.AsyncClient(timeout=60.0) as client:
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
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported model: {request.model}"
            )

        logger.info("Chat completed")

        return {
            "answer": answer,
            "context_chunks": len(results),
            "sources": [
                {
                    "text": (r if isinstance(r, str) else str(r))[:200] + "...",
                    "score": 1.0
                }
                for r in results
            ]
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/reset")
async def reset_memory():
    """Reset memory"""
    try:
        if VIDEO_PATH.exists():
            VIDEO_PATH.unlink()
        if INDEX_PATH.exists():
            INDEX_PATH.unlink()
        if METADATA_PATH.exists():
            METADATA_PATH.unlink()

        for file in UPLOAD_DIR.glob("*"):
            if file.is_file():
                file.unlink()

        logger.info("Memory reset")

        return {"success": True, "message": "Memory reset successfully"}

    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8503)
