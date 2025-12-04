"""
Script 93: Automated RAGFlow Upload
Uploads 24 files from rag_package to RAGFlow, creates dataset and chat assistant
Usage: python scripts/93_upload_to_ragflow.py --api-key YOUR_API_KEY
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Check for ragflow-sdk
try:
    from ragflow_sdk import RAGFlow
except ImportError:
    print("[FAIL] ragflow-sdk not installed. Run: pip install ragflow-sdk")
    sys.exit(1)

# Configuration
BASE_DIR = Path(__file__).parent.parent
RAG_PACKAGE_DIR = BASE_DIR / "data" / "rag_package"
MANIFEST_FILE = RAG_PACKAGE_DIR / "ingestion_manifest.json"
RAGFLOW_BASE_URL = "https://ragflow.srv759970.hstgr.cloud"

# Dataset Configuration
DATASET_CONFIG = {
    "name": "DownTo40_Sources_2024",
    "description": "Complete documentation and sources for DownTo40 electricity market analysis project",
    "permission": "me",
    "chunk_method": "general"
}

# Chat Assistant Configuration
CHAT_CONFIG = {
    "name": "DownTo40 Sources Q&A",
    "llm": {
        "model_name": "gpt-4",
        "temperature": 0.2,
        "top_p": 0.3
    },
    "prompt": {
        "similarity_threshold": 0.2,
        "top_n": 8,
        "show_quote": True,
        "system": """You are an expert assistant helping answer questions about the DownTo40 electricity market analysis project.

Use the provided documents to answer questions about:
- Data sources and scraping methodologies
- Business model validation
- Technical implementation details
- Sprint results and metrics
- Official sources (ENTSO-E, RTE, Electricity Maps)

Always cite the specific document and section when answering.
If information is not in the documents, say so explicitly.
Be precise with numbers and dates."""
    }
}


def load_manifest():
    """Load ingestion manifest"""
    if not MANIFEST_FILE.exists():
        print(f"[FAIL] Manifest not found: {MANIFEST_FILE}")
        sys.exit(1)

    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def initialize_client(api_key):
    """Initialize RAGFlow client"""
    print(f"[INFO] Connecting to RAGFlow: {RAGFLOW_BASE_URL}")
    try:
        rag = RAGFlow(api_key=api_key, base_url=RAGFLOW_BASE_URL)
        print("[OK] Connected to RAGFlow")
        return rag
    except Exception as e:
        print(f"[FAIL] Failed to connect: {e}")
        sys.exit(1)


def create_or_get_dataset(rag, manifest):
    """Create dataset or retrieve existing one"""
    print(f"\n[INFO] Creating dataset: {DATASET_CONFIG['name']}")

    try:
        # Check if dataset already exists
        datasets = rag.list_datasets(page=1, page_size=100)
        for ds in datasets:
            if ds.name == DATASET_CONFIG['name']:
                print(f"[INFO] Dataset already exists (ID: {ds.id})")
                return ds

        # Create new dataset
        dataset = rag.create_dataset(**DATASET_CONFIG)
        print(f"[OK] Dataset created (ID: {dataset.id})")
        return dataset

    except Exception as e:
        print(f"[FAIL] Failed to create dataset: {e}")
        sys.exit(1)


def upload_documents_to_dataset(dataset, manifest):
    """Upload all documents from manifest"""
    print(f"\n[INFO] Uploading {manifest['total_files']} files...")

    uploaded = 0
    failed = []

    # Iterate through categories
    for category_name, category_data in manifest['categories'].items():
        print(f"\n[INFO] Category: {category_name.upper()} ({category_data['file_count']} files)")

        for file_info in category_data['files']:
            file_path = BASE_DIR / file_info['rag_path']
            display_name = file_info['filename']

            print(f"   Uploading {display_name}...", end='')

            try:
                # Read file as binary
                with open(file_path, 'rb') as f:
                    blob = f.read()

                # Upload
                dataset.upload_documents([{
                    "display_name": display_name,
                    "blob": blob
                }])

                print(f" [OK] ({file_info['size_mb']} MB)")
                uploaded += 1

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f" [FAIL] {e}")
                failed.append(display_name)

    # Upload MASTER_CONTEXT.md (critical document)
    master_context_path = BASE_DIR / manifest['master_context']
    if master_context_path.exists():
        print(f"\n[INFO] Uploading MASTER_CONTEXT.md...", end='')
        try:
            with open(master_context_path, 'rb') as f:
                blob = f.read()

            dataset.upload_documents([{
                "display_name": "MASTER_CONTEXT.md",
                "blob": blob
            }])
            print(" [OK]")
            uploaded += 1
        except Exception as e:
            print(f" [FAIL] {e}")
            failed.append("MASTER_CONTEXT.md")

    # Summary
    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"[OK] Uploaded: {uploaded}/{manifest['total_files'] + 1}")
    print(f"[FAIL] Failed: {len(failed)}")

    if failed:
        print("\n[WARN] Failed files:")
        for filename in failed:
            print(f"   - {filename}")

    return uploaded, failed


def parse_documents(dataset):
    """Parse all uploaded documents"""
    print("\n[INFO] Starting document parsing...")

    try:
        # Get all documents
        docs = dataset.list_documents(page=1, page_size=100)
        doc_ids = [doc.id for doc in docs]

        print(f"[INFO] Parsing {len(doc_ids)} documents...")

        # Asynchronous parsing
        dataset.async_parse_documents(doc_ids)

        print("[INFO] Parsing started (asynchronous)")
        print("[INFO] Documents will be indexed in background (~2-5 minutes)")

        return len(doc_ids)

    except Exception as e:
        print(f"[FAIL] Failed to parse documents: {e}")
        return 0


def create_chat_assistant(rag, dataset):
    """Create chat assistant"""
    print("\n[INFO] Creating chat assistant...")

    try:
        # Check if chat already exists
        chats = rag.list_chats(page=1, page_size=100)
        for chat in chats:
            if chat.name == CHAT_CONFIG['name']:
                print(f"[INFO] Chat already exists (ID: {chat.id})")
                print(f"[INFO] Chat URL: {RAGFLOW_BASE_URL}/chat/{chat.id}")
                return chat

        # Create new chat
        assistant = rag.create_chat(
            name=CHAT_CONFIG['name'],
            dataset_ids=[dataset.id],
            llm=CHAT_CONFIG['llm'],
            prompt=CHAT_CONFIG['prompt']
        )

        print(f"[OK] Chat assistant created (ID: {assistant.id})")
        print(f"\n[INFO] Public Chat URL:")
        print(f"   {RAGFLOW_BASE_URL}/chat/{assistant.id}")

        return assistant

    except Exception as e:
        print(f"[FAIL] Failed to create chat: {e}")
        return None


def save_ragflow_metadata(dataset, assistant):
    """Save RAGFlow IDs and URLs for later use"""
    metadata = {
        "created_at": datetime.now().isoformat(),
        "ragflow_url": RAGFLOW_BASE_URL,
        "dataset": {
            "id": dataset.id,
            "name": dataset.name
        },
        "chat": {
            "id": assistant.id if assistant else None,
            "name": assistant.name if assistant else None,
            "url": f"{RAGFLOW_BASE_URL}/chat/{assistant.id}" if assistant else None
        }
    }

    output_file = BASE_DIR / "data" / "ragflow_metadata.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Metadata saved to: {output_file}")
    return metadata


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Automated RAGFlow Upload')
    parser.add_argument('--api-key', required=True, help='RAGFlow API key')
    parser.add_argument('--skip-upload', action='store_true', help='Skip file upload (only create chat)')

    args = parser.parse_args()

    print("=" * 80)
    print("RAGFLOW AUTOMATED UPLOAD")
    print("=" * 80)

    # Load manifest
    manifest = load_manifest()
    print(f"[INFO] Manifest loaded: {manifest['total_files']} files ({manifest['total_size_mb']:.2f} MB)")

    # Initialize client
    rag = initialize_client(args.api_key)

    # Create dataset
    dataset = create_or_get_dataset(rag, manifest)

    # Upload documents
    if not args.skip_upload:
        uploaded, failed = upload_documents_to_dataset(dataset, manifest)

        if uploaded > 0:
            # Parse documents
            parsed_count = parse_documents(dataset)
    else:
        print("\n[SKIP] Document upload skipped (--skip-upload flag)")

    # Create chat assistant
    assistant = create_chat_assistant(rag, dataset)

    # Save metadata
    if assistant:
        metadata = save_ragflow_metadata(dataset, assistant)

    # Next steps
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Wait 2-5 minutes for document parsing to complete")
    print("2. Verify parsing status in RAGFlow UI")
    print(f"   URL: {RAGFLOW_BASE_URL}")
    print("\n3. Test the chat with sample queries:")
    print("   - D'où viennent les 27.93 TWh exportés?")
    print("   - Combien de dates ont été scrappées?")
    print("   - Quelle est la méthodologie ENTSO-E?")

    if assistant:
        print(f"\n4. Update Streamlit page with chat URL:")
        print(f"   pages/1_Sources_Documentation.py")
        print(f"   RAGFLOW_CHAT_URL = \"{RAGFLOW_BASE_URL}/chat/{assistant.id}\"")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
