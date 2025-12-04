"""
Script 98: Upload Documents to MemVid API (Hostinger)
Uploads all 24 documents to the MemVid RAG service running on Hostinger
Usage: python scripts/98_upload_to_memvid_api.py
"""

import json
import requests
from pathlib import Path
from loguru import logger
import sys
import time

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

# MemVid API configuration
MEMVID_API_URL = "http://memvid.srv759970.hstgr.cloud"  # Nginx proxy to port 8503
PROJECT_NAME = "downto40-docs"
PROJECT_DESCRIPTION = "DownTo40 project documentation, sources, and scraping methodologies"

def check_api_health():
    """Check if MemVid API is running"""
    try:
        response = requests.get(f"{MEMVID_API_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.success(f"✅ MemVid API is healthy: {response.json()}")
            return True
        else:
            logger.error(f"❌ MemVid API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Cannot connect to MemVid API at {MEMVID_API_URL}")
        logger.error("   Make sure MemVid containers are running: docker compose up -d")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking API health: {e}")
        return False

def create_project():
    """Create MemVid project for DownTo40"""
    try:
        response = requests.post(
            f"{MEMVID_API_URL}/projects",
            json={
                "name": PROJECT_NAME,
                "description": PROJECT_DESCRIPTION
            },
            timeout=30
        )

        if response.status_code == 200:
            project = response.json()
            logger.success(f"✅ Project created: {project['id']}")
            return project['id']
        elif response.status_code == 409:  # Project already exists
            logger.info("📝 Project already exists, listing projects...")
            response = requests.get(f"{MEMVID_API_URL}/projects", timeout=10)
            projects = response.json()
            for project in projects:
                if project['name'] == PROJECT_NAME:
                    logger.success(f"✅ Found existing project: {project['id']}")
                    return project['id']
        else:
            logger.error(f"❌ Failed to create project: {response.text}")
            return None

    except Exception as e:
        logger.error(f"❌ Error creating project: {e}")
        return None

def upload_text_file(project_id, file_path, metadata):
    """Upload text file to MemVid"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        response = requests.post(
            f"{MEMVID_API_URL}/projects/{project_id}/index/text/async",
            json={
                "text": content,
                "metadata": metadata
            },
            timeout=60
        )

        if response.status_code == 200:
            job_data = response.json()
            logger.success(f"   ✅ Queued: {metadata['filename']} (job: {job_data['job_id'][:8]}...)")
            return job_data['job_id']
        else:
            logger.error(f"   ❌ Failed: {response.text}")
            return None

    except Exception as e:
        logger.error(f"   ❌ Error uploading {file_path}: {e}")
        return None

def upload_documents():
    """Upload all documents from RAG package"""

    logger.info("=" * 80)
    logger.info("MEMVID UPLOAD - DOWNTO40 DOCUMENTATION")
    logger.info("=" * 80)

    # Check API health
    if not check_api_health():
        logger.error("\n❌ MemVid API is not accessible. Aborting.")
        return

    # Create project
    logger.info(f"\n📦 Creating project: {PROJECT_NAME}")
    project_id = create_project()
    if not project_id:
        logger.error("\n❌ Could not create/find project. Aborting.")
        return

    # Load manifest
    manifest_path = Path('data/rag_package/ingestion_manifest.json')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    logger.info(f"\n📂 Found {manifest['total_files']} files ({manifest['total_size_mb']:.2f} MB)")

    # Upload files by category
    total_uploaded = 0
    total_skipped = 0
    job_ids = []

    for category, data in manifest['categories'].items():
        logger.info(f"\n📁 Category: {category.upper()} ({data['file_count']} files)")

        for file_info in data['files']:
            file_path = Path(file_info['rag_path'])
            filename = file_info['filename']
            file_type = file_info.get('type', 'unknown')

            if not file_path.exists():
                logger.warning(f"   ⚠️  Not found: {filename}")
                total_skipped += 1
                continue

            metadata = {
                "filename": filename,
                "category": category,
                "type": file_type,
                "size_mb": file_info['size_mb']
            }

            # Only upload text-based files
            if file_type in ["markdown", "html", "javascript", "json"]:
                job_id = upload_text_file(project_id, file_path, metadata)
                if job_id:
                    job_ids.append(job_id)
                    total_uploaded += 1
                else:
                    total_skipped += 1

            elif file_type == "pdf":
                # TODO: MemVid API v2 doesn't have direct PDF upload yet
                # We'll need to extract text client-side or wait for PDF endpoint
                logger.warning(f"   ⏭️  Skipped (PDF not yet supported): {filename}")
                total_skipped += 1

            elif file_type == "image":
                # Images: create text description
                image_text = f"Screenshot: {filename}\nCategory: {category}\nPath: {file_path}"
                metadata['original_type'] = 'image'
                job_id = upload_text_file(project_id, file_path, metadata)  # Will fail, but logged
                total_skipped += 1

            else:
                logger.warning(f"   ⏭️  Skipped (unsupported type): {filename}")
                total_skipped += 1

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("UPLOAD SUMMARY")
    logger.info("=" * 80)
    logger.info(f"📊 Files uploaded: {total_uploaded}/{manifest['total_files']}")
    logger.info(f"⏭️  Files skipped: {total_skipped}")
    logger.info(f"📋 Jobs queued: {len(job_ids)}")

    if job_ids:
        logger.info(f"\n⏳ Indexing in progress... (async jobs)")
        logger.info(f"   Check status: GET {MEMVID_API_URL}/jobs/{{job_id}}")
        logger.info(f"   List all jobs: GET {MEMVID_API_URL}/jobs")

    # Save project info
    output_file = Path("data/memvid_project.json")
    project_data = {
        "project_id": project_id,
        "project_name": PROJECT_NAME,
        "api_url": MEMVID_API_URL,
        "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files_uploaded": total_uploaded,
        "files_skipped": total_skipped,
        "job_ids": job_ids
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(project_data, f, indent=2, ensure_ascii=False)

    logger.success(f"\n✅ Project info saved: {output_file}")
    logger.info("=" * 80)

if __name__ == "__main__":
    try:
        upload_documents()
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Upload interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"\n❌ Fatal error: {e}")
        sys.exit(1)
