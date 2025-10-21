"""
Data models for MemVid RAG API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class ProjectConfig(BaseModel):
    """Project configuration"""
    chunk_size: int = Field(512, ge=128, le=4096)
    chunk_overlap: int = Field(64, ge=0, le=512)


class Project(BaseModel):
    """Project model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    total_chunks: int = 0
    video_size_mb: float = 0.0
    files_count: int = 0
    config: ProjectConfig = Field(default_factory=ProjectConfig)


class ProjectCreate(BaseModel):
    """Create project request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    config: Optional[ProjectConfig] = None


class ProjectUpdate(BaseModel):
    """Update project request"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    config: Optional[ProjectConfig] = None


class IndexTextRequest(BaseModel):
    """Index text request"""
    text: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IndexFolderRequest(BaseModel):
    """Index folder request"""
    folder_path: str = Field(..., min_length=1)
    recursive: bool = Field(True)
    file_extensions: List[str] = Field(default_factory=lambda: [".txt", ".md", ".pdf"])
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None


class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=50)


class SearchResult(BaseModel):
    """Search result"""
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Chat request"""
    query: str = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=20)
    model: str = Field("ollama", description="LLM to use: ollama, openai")
    ollama_model: str = Field("qwen2.5:14b")
    ollama_base_url: str = Field("http://69.62.108.82:11434")
    openai_api_key: Optional[str] = None
    openai_model: str = Field("gpt-3.5-turbo")
    openai_base_url: Optional[str] = None  # For Azure or custom endpoints


class ChatResponse(BaseModel):
    """Chat response"""
    answer: str
    context_chunks: int
    sources: List[Dict[str, Any]]


class ProjectStats(BaseModel):
    """Project statistics"""
    id: str
    name: str
    total_chunks: int
    video_size_mb: float
    files_count: int
    last_updated: Optional[datetime]
