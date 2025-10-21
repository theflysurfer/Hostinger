"""
Project manager for multi-project RAG system
"""
from pathlib import Path
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from .models import Project, ProjectCreate, ProjectUpdate, ProjectConfig


class ProjectManager:
    """Manage multiple RAG projects"""

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.projects_dir = self.base_dir / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.projects_file = self.base_dir / "projects.json"

        # Load or create projects index
        self.projects: Dict[str, Project] = {}
        self._load_projects()

    def _load_projects(self):
        """Load projects from file"""
        if self.projects_file.exists():
            try:
                with open(self.projects_file, "r") as f:
                    data = json.load(f)
                    self.projects = {
                        p["id"]: Project(**p) for p in data
                    }
                logger.info(f"Loaded {len(self.projects)} projects")
            except Exception as e:
                logger.error(f"Failed to load projects: {e}")
                self.projects = {}
        else:
            self.projects = {}

    def _save_projects(self):
        """Save projects to file"""
        try:
            data = [p.model_dump(mode="json") for p in self.projects.values()]
            with open(self.projects_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Saved {len(self.projects)} projects")
        except Exception as e:
            logger.error(f"Failed to save projects: {e}")
            raise

    def create_project(self, request: ProjectCreate) -> Project:
        """Create a new project"""
        project = Project(
            name=request.name,
            description=request.description,
            tags=request.tags,
            config=request.config if request.config else ProjectConfig()
        )

        # Create project directory
        project_dir = self.projects_dir / project.id
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "files").mkdir(exist_ok=True)

        # Save project metadata
        self.projects[project.id] = project
        self._save_projects()

        logger.info(f"Created project: {project.name} ({project.id})")
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID"""
        return self.projects.get(project_id)

    def list_projects(self) -> List[Project]:
        """List all projects"""
        return list(self.projects.values())

    def update_project(self, project_id: str, request: ProjectUpdate) -> Optional[Project]:
        """Update project"""
        project = self.projects.get(project_id)
        if not project:
            return None

        if request.name is not None:
            project.name = request.name
        if request.description is not None:
            project.description = request.description
        if request.tags is not None:
            project.tags = request.tags
        if request.config is not None:
            project.config = request.config

        project.updated_at = datetime.now()
        self._save_projects()

        logger.info(f"Updated project: {project.name} ({project.id})")
        return project

    def delete_project(self, project_id: str) -> bool:
        """Delete project"""
        if project_id not in self.projects:
            return False

        # Delete project directory
        project_dir = self.projects_dir / project_id
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)

        # Remove from index
        project_name = self.projects[project_id].name
        del self.projects[project_id]
        self._save_projects()

        logger.info(f"Deleted project: {project_name} ({project_id})")
        return True

    def get_project_dir(self, project_id: str) -> Path:
        """Get project directory path"""
        return self.projects_dir / project_id

    def get_project_video_path(self, project_id: str) -> Path:
        """Get project video file path"""
        return self.get_project_dir(project_id) / "memory.mp4"

    def get_project_index_path(self, project_id: str) -> Path:
        """Get project index file path"""
        return self.get_project_dir(project_id) / "memory_index.json"

    def get_project_files_dir(self, project_id: str) -> Path:
        """Get project files directory"""
        return self.get_project_dir(project_id) / "files"

    def update_project_stats(self, project_id: str, total_chunks: int, video_size_mb: float, files_count: int):
        """Update project statistics"""
        project = self.projects.get(project_id)
        if project:
            project.total_chunks = total_chunks
            project.video_size_mb = video_size_mb
            project.files_count = files_count
            project.updated_at = datetime.now()
            self._save_projects()
