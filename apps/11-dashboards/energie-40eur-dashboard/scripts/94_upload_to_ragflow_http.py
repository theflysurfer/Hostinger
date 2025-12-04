"""
Script 94: Upload to RAGFlow via HTTP API (no SDK)
Alternative to script 93 for self-hosted instances without SDK support
Uses direct HTTP requests with login/password authentication
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
RAGFLOW_BASE_URL = "http://69.62.108.82:9500"  # Internal Docker port

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
        "layout_recognize": True,
        "raptor": {"use_raptor": False}
    }
}


class RAGFlowClient:
    """Simple RAGFlow HTTP client"""

    def __init__(self, base_url, email, password):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.token = None
        self.user_id = None

    def login(self):
        """Login and get authorization token"""
        print(f"[INFO] Logging in as {self.email}...")

        url = f"{self.base_url}/v1/user/login"
        data = {
            "email": self.email,
            "password": self.password
        }

        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()

            if result.get('code') == 0:
                self.token = result['data']['access_token']
                self.user_id = result['data'].get('user_id')
                self.session.headers.update({'Authorization': f'Bearer {self.token}'})
                print("[OK] Logged in successfully")
                return True
            else:
                print(f"[FAIL] Login failed: {result.get('message')}")
                return False

        except Exception as e:
            print(f"[FAIL] Login error: {e}")
            return False

    def create_dataset(self, config):
        """Create knowledge base dataset"""
        print(f"\n[INFO] Creating dataset: {config['name']}")

        url = f"{self.base_url}/v1/dataset"

        try:
            response = self.session.post(url, json=config, timeout=10)
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

    def list_datasets(self):
        """List all datasets"""
        url = f"{self.base_url}/v1/dataset?page=1&page_size=100"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            result = response.json()

            if result.get('code') == 0:
                return result['data']
            else:
                return []

        except Exception as e:
            print(f"[WARN] List datasets error: {e}")
            return []

    def upload_document(self, dataset_id, file_path, display_name):
        """Upload a single document"""
        url = f"{self.base_url}/v1/dataset/{dataset_id}/document"

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (display_name, f)}
                response = self.session.post(url, files=files, timeout=60)
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

    def parse_documents(self, dataset_id, document_ids):
        """Trigger document parsing"""
        url = f"{self.base_url}/v1/dataset/{dataset_id}/chunk"
        data = {"document_ids": document_ids}

        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result.get('code') == 0

        except Exception as e:
            print(f"[WARN] Parse error: {e}")
            return False

    def create_chat(self, name, dataset_ids, config):
        """Create chat assistant"""
        url = f"{self.base_url}/v1/chat"

        data = {
            "name": name,
            "dataset_ids": dataset_ids,
            **config
        }

        try:
            response = self.session.post(url, json=data, timeout=10)
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


def load_manifest():
    """Load ingestion manifest"""
    if not MANIFEST_FILE.exists():
        print(f"[FAIL] Manifest not found: {MANIFEST_FILE}")
        sys.exit(1)

    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def upload_all_documents(client, dataset_id, manifest):
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

            doc_id = client.upload_document(dataset_id, file_path, display_name)

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
        doc_id = client.upload_document(dataset_id, master_context_path, "MASTER_CONTEXT.md")
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
        "ragflow_url": RAGFLOW_BASE_URL,
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

    parser = argparse.ArgumentParser(description='Upload to RAGFlow via HTTP API')
    parser.add_argument('--email', required=True, help='RAGFlow email')
    parser.add_argument('--password', required=True, help='RAGFlow password')

    args = parser.parse_args()

    print("=" * 80)
    print("RAGFLOW HTTP API UPLOAD")
    print("=" * 80)

    # Load manifest
    manifest = load_manifest()
    print(f"[INFO] Manifest loaded: {manifest['total_files']} files ({manifest['total_size_mb']:.2f} MB)")

    # Initialize client
    client = RAGFlowClient(RAGFLOW_BASE_URL, args.email, args.password)

    if not client.login():
        print("\n[FAIL] Authentication failed. Check email/password.")
        sys.exit(1)

    # Check if dataset exists
    datasets = client.list_datasets()
    existing_dataset = None
    for ds in datasets:
        if ds.get('name') == DATASET_CONFIG['name']:
            existing_dataset = ds['id']
            print(f"\n[INFO] Dataset already exists (ID: {existing_dataset})")
            break

    # Create or use existing dataset
    dataset_id = existing_dataset or client.create_dataset(DATASET_CONFIG)

    if not dataset_id:
        print("\n[FAIL] Could not create/access dataset")
        sys.exit(1)

    # Upload documents
    uploaded_ids, failed = upload_all_documents(client, dataset_id, manifest)

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
        if client.parse_documents(dataset_id, uploaded_ids):
            print("[OK] Parsing started")
        else:
            print("[WARN] Could not trigger parsing")

    # Create chat
    chat_config = {
        "llm": {"model_name": "gpt-4", "temperature": 0.2},
        "prompt": {
            "similarity_threshold": 0.2,
            "top_n": 8,
            "system": "You are an expert assistant for DownTo40 electricity market analysis project."
        }
    }

    chat_id = client.create_chat("DownTo40 Sources Q&A", [dataset_id], chat_config)

    # Save metadata
    if chat_id:
        metadata = save_metadata(dataset_id, chat_id)
        print(f"\n[INFO] Chat URL: {metadata['chat']['url']}")

    print("\n" + "=" * 80)
    print("[INFO] Upload complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
