"""
Script 97: Create MemVid Index for DownTo40 Documentation
Indexes all 24 documents (PDFs, Markdown, HTML, JSON, JS) into a searchable MP4 video file
Usage: python scripts/97_create_memvid_index.py
"""

import json
from pathlib import Path
from memvid import MemvidEncoder
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add("data/memvid_indexing.log", rotation="10 MB", retention="7 days", level="DEBUG")

def load_manifest():
    """Load ingestion manifest"""
    manifest_path = Path('data/rag_package/ingestion_manifest.json')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_text_file(file_path):
    """Read text file with encoding detection"""
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    logger.warning(f"Failed to read {file_path} with any encoding")
    return None

def index_documents():
    """Index all documents from RAG package into MemVid"""

    logger.info("=" * 80)
    logger.info("MEMVID INDEXING - DOWNTO40 DOCUMENTATION")
    logger.info("=" * 80)

    # Load manifest
    manifest = load_manifest()
    logger.info(f"Loaded manifest: {manifest['total_files']} files ({manifest['total_size_mb']:.2f} MB)")

    # Initialize encoder with optimized settings
    logger.info("Initializing MemVid encoder...")
    encoder = MemvidEncoder(
        chunk_size=512,  # Optimal for Q&A retrieval
        chunk_overlap=50  # Some context overlap
    )

    # Process files by category
    total_indexed = 0
    total_skipped = 0

    for category, data in manifest['categories'].items():
        logger.info(f"\n📂 Processing category: {category.upper()} ({data['file_count']} files)")

        for file_info in data['files']:
            file_path = Path(file_info['rag_path'])
            filename = file_info['filename']
            file_type = file_info.get('type', 'unknown')

            if not file_path.exists():
                logger.warning(f"⚠️  File not found: {filename}")
                total_skipped += 1
                continue

            try:
                metadata = {
                    "filename": filename,
                    "category": category,
                    "type": file_type,
                    "size_mb": file_info['size_mb']
                }

                # Handle different file types
                if file_type == "pdf":
                    logger.info(f"   📄 Indexing PDF: {filename}")
                    encoder.add_pdf(str(file_path), metadata=metadata)

                elif file_type in ["markdown", "html", "javascript", "json"]:
                    logger.info(f"   📝 Indexing {file_type}: {filename}")
                    content = read_text_file(file_path)
                    if content:
                        encoder.add_text(content, metadata=metadata)
                    else:
                        logger.warning(f"   ⚠️  Skipped (read error): {filename}")
                        total_skipped += 1
                        continue

                elif file_type == "image":
                    # Images stored as metadata reference only (not actual image data)
                    logger.info(f"   🖼️  Indexing image metadata: {filename}")
                    image_text = f"Screenshot: {filename}\nCategory: {category}\nPath: {file_path}"
                    encoder.add_text(image_text, metadata=metadata)

                else:
                    logger.warning(f"   ⚠️  Unknown type '{file_type}': {filename}")
                    total_skipped += 1
                    continue

                total_indexed += 1
                logger.success(f"   ✅ Indexed: {filename}")

            except Exception as e:
                logger.error(f"   ❌ Error indexing {filename}: {e}")
                total_skipped += 1

    # Build video
    logger.info("\n" + "=" * 80)
    logger.info("🎬 BUILDING MEMVID VIDEO...")
    logger.info("=" * 80)

    output_video = "data/downto40_knowledge.mp4"
    output_index = "data/downto40_knowledge_index.json"

    logger.info(f"Output video: {output_video}")
    logger.info(f"Output index: {output_index}")
    logger.info("This may take 2-5 minutes...")

    encoder.build_video(
        output_video,
        output_index,
        fps=30,  # Standard frame rate
        video_codec='h264',  # Compatible with all browsers
        crf=23  # Good quality/size tradeoff
    )

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("✅ INDEXING COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"📊 Files indexed: {total_indexed}/{manifest['total_files']}")
    logger.info(f"⚠️  Files skipped: {total_skipped}")
    logger.info(f"📦 Video file: {output_video}")
    logger.info(f"📝 Index file: {output_index}")

    # File sizes
    video_path = Path(output_video)
    index_path = Path(output_index)
    if video_path.exists():
        video_size_mb = video_path.stat().st_size / (1024 * 1024)
        logger.info(f"💾 Video size: {video_size_mb:.2f} MB")
    if index_path.exists():
        index_size_kb = index_path.stat().st_size / 1024
        logger.info(f"📋 Index size: {index_size_kb:.2f} KB")

    logger.info("\n🎉 MemVid knowledge base ready for Streamlit integration!")
    logger.info("=" * 80)

    return {
        "video_path": output_video,
        "index_path": output_index,
        "total_indexed": total_indexed,
        "total_skipped": total_skipped
    }

if __name__ == "__main__":
    try:
        # Check dependencies
        try:
            import PyPDF2
            logger.info("✅ PyPDF2 installed")
        except ImportError:
            logger.error("❌ PyPDF2 not installed. Run: pip install PyPDF2")
            sys.exit(1)

        # Run indexing
        result = index_documents()

        logger.success(f"\n✅ Success! {result['total_indexed']} documents indexed into MemVid")

    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Indexing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"\n❌ Fatal error: {e}")
        sys.exit(1)
