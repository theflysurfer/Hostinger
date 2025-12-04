"""
Script 95: Direct RAGFlow API Upload (no SDK required)
Uses REST API directly with API key authentication
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent.parent
RAG_PACKAGE_DIR = BASE_DIR / "data" / "rag_package"
MANIFEST_FILE = RAG_PACKAGE_DIR / "ingestion_manifest.json"
RAGFLOW_BASE_URL = "https://ragflow.srv759970.hstgr.cloud/v1"

# Dataset Configuration
DATASET_CONFIG = {
    "name": "DownTo40_Sources_2024",
    "description": "Complete documentation and sources for DownTo40 electricity market analysis project",
    "permission": "me",
    "language": "French",
    "chunk_method": "naive",
    "parser_config": {
        "chunk_token_count": 1024,
        "delimiter": "\n!?。；！？",
        "html4excel": False,
        "layout_recognize": True
    }
}


def load_manifest():
    """Load ingestion manifest"""
    if not MANIFEST_FILE.exists():
        print(f"[FAIL] Manifest not found: {MANIFEST_FILE}")
        sys.exit(1)

    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_dataset(api_key, config):
    """Create knowledge base dataset"""
    print(f"\n[INFO] Creating dataset: {config['name']}")

    url = f"{RAGFLOW_BASE_URL}/dataset"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=config, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()

        if result.get('code') == 0:
            dataset_id = result['data']['dataset_id']
            print(f"[OK] Dataset created (ID: {dataset_id})")
            return dataset_id
        else:
            print(f"[FAIL] Dataset creation failed: {result.get('message')}")
            return None

    except Exception as e:
        print(f"[FAIL] Dataset creation error: {e}")
        return None


def list_datasets(api_key):
    """List all datasets"""
    url = f"{RAGFLOW_BASE_URL}/dataset?page=1&page_size=100"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        result = response.json()

        if result.get('code') == 0:
            return result['data']
        else:
            return []

    except Exception as e:
        print(f"[WARN] List datasets error: {e}")
        return []


def upload_document(api_key, dataset_id, file_path, display_name):
    """Upload a single document"""
    url = f"{RAGFLOW_BASE_URL}/dataset/{dataset_id}/document"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (display_name, f)}
            response = requests.post(url, files=files, headers=headers, timeout=60)
            response.raise_for_status()

        result = response.json()

        if result.get('code') == 0:
            return result['data']['document_id']
        else:
            print(f"[WARN] Upload warning: {result.get('message')}")
            return None

    except Exception as e:
        print(f"[FAIL] Upload error: {e}")
        return None


def parse_documents(api_key, dataset_id, document_ids):
    """Trigger document parsing"""
    url = f"{RAGFLOW_BASE_URL}/dataset/{dataset_id}/chunk"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {"document_ids": document_ids}

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()

        result = response.json()
        return result.get('code') == 0

    except Exception as e:
        print(f"[WARN] Parse error: {e}")
        return False


def create_chat(api_key, name, dataset_ids):
    """Create chat assistant"""
    url = f"{RAGFLOW_BASE_URL}/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "name": name,
        "dataset_ids": dataset_ids,
        "llm": {"model_name": "gpt-4", "temperature": 0.2},
        "prompt": {
            "similarity_threshold": 0.2,
            "top_n": 8,
            "system": "You are an expert assistant for DownTo40 electricity market analysis project."
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()

        result = response.json()

        if result.get('code') == 0:
            chat_id = result['data']['id']
            print(f"[OK] Chat created (ID: {chat_id})")
            return chat_id
        else:
            print(f"[FAIL] Chat creation failed: {result.get('message')}")
            return None

    except Exception as e:
        print(f"[FAIL] Chat creation error: {e}")
        return None


def upload_all_documents(api_key, dataset_id, manifest):
    """Upload all documents from manifest"""
    print(f"\n[INFO] Uploading {manifest['total_files']} files...")

    uploaded = []
    failed = []

    # Iterate through categories
    for category_name, category_data in manifest['categories'].items():
        print(f"\n[INFO] Category: {category_name.upper()} ({category_data['file_count']} files)")

        for file_info in category_data['files']:
            file_path = BASE_DIR / file_info['rag_path']
            display_name = file_info['filename']

            print(f"   Uploading {display_name}...", end='', flush=True)

            doc_id = upload_document(api_key, dataset_id, file_path, display_name)

            if doc_id:
                print(f" [OK] ({file_info['size_mb']} MB)")
                uploaded.append(doc_id)
            else:
                print(f" [FAIL]")
                failed.append(display_name)

            # Rate limiting
            time.sleep(1)

    # Upload MASTER_CONTEXT.md
    master_context_path = BASE_DIR / manifest['master_context']
    if master_context_path.exists():
        print(f"\n[INFO] Uploading MASTER_CONTEXT.md...", end='', flush=True)
        doc_id = upload_document(api_key, dataset_id, master_context_path, "MASTER_CONTEXT.md")
        if doc_id:
            print(" [OK]")
            uploaded.append(doc_id)
        else:
            print(" [FAIL]")
            failed.append("MASTER_CONTEXT.md")

    return uploaded, failed


def save_metadata(dataset_id, chat_id):
    """Save RAGFlow metadata"""
    metadata = {
        "created_at": datetime.now().isoformat(),
        "ragflow_url": RAGFLOW_BASE_URL.replace('/v1', ''),
        "dataset": {
            "id": dataset_id,
            "name": DATASET_CONFIG['name']
        },
        "chat": {
            "id": chat_id,
            "name": "DownTo40 Sources Q&A",
            "url": f"https://ragflow.srv759970.hstgr.cloud/chat/{chat_id}" if chat_id else None
        }
    }

    output_file = BASE_DIR / "data" / "ragflow_metadata.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Metadata saved to: {output_file}")
    return metadata


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Upload to RAGFlow via Direct REST API')
    parser.add_argument('--api-key', required=True, help='RAGFlow API key')

    args = parser.parse_args()

    print("=" * 80)
    print("RAGFLOW DIRECT API UPLOAD")
    print("=" * 80)

    # Load manifest
    manifest = load_manifest()
    print(f"[INFO] Manifest loaded: {manifest['total_files']} files ({manifest['total_size_mb']:.2f} MB)")

    # Check if dataset exists
    datasets = list_datasets(args.api_key)
    existing_dataset = None
    for ds in datasets:
        if ds.get('name') == DATASET_CONFIG['name']:
            existing_dataset = ds['id']
            print(f"\n[INFO] Dataset already exists (ID: {existing_dataset})")
            break

    # Create or use existing dataset
    dataset_id = existing_dataset or create_dataset(args.api_key, DATASET_CONFIG)

    if not dataset_id:
        print("\n[FAIL] Could not create/access dataset")
        sys.exit(1)

    # Upload documents
    uploaded_ids, failed = upload_all_documents(args.api_key, dataset_id, manifest)

    # Summary
    print("\n" + "=" * 80)
    print("UPLOAD SUMMARY")
    print("=" * 80)
    print(f"[OK] Uploaded: {len(uploaded_ids)}/{manifest['total_files'] + 1}")
    print(f"[FAIL] Failed: {len(failed)}")

    if failed:
        print("\n[WARN] Failed files:")
        for filename in failed:
            print(f"   - {filename}")

    # Parse documents
    if uploaded_ids:
        print(f"\n[INFO] Triggering parsing for {len(uploaded_ids)} documents...")
        if parse_documents(args.api_key, dataset_id, uploaded_ids):
            print("[OK] Parsing started")
        else:
            print("[WARN] Could not trigger parsing")

    # Create chat
    chat_id = create_chat(args.api_key, "DownTo40 Sources Q&A", [dataset_id])

    # Save metadata
    if chat_id:
        metadata = save_metadata(dataset_id, chat_id)
        print(f"\n[INFO] Chat URL: {metadata['chat']['url']}")

    print("\n" + "=" * 80)
    print("[INFO] Upload complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
