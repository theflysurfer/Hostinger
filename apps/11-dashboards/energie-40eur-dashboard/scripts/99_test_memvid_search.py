"""
Script 99: Test MemVid Search API
Tests semantic search functionality on the downto40-docs project
Usage: python scripts/99_test_memvid_search.py
"""

import json
import requests
from pathlib import Path
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

def load_project_config():
    """Load MemVid project configuration"""
    config_path = Path('data/memvid_project.json')
    if not config_path.exists():
        logger.error(f"❌ Configuration file not found: {config_path}")
        logger.info("   Run: python scripts/98_upload_to_memvid_api.py")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_search(api_url, project_id, query, top_k=5):
    """Test semantic search"""
    logger.info(f"\n🔍 Query: \"{query}\"")

    try:
        response = requests.post(
            f"{api_url}/projects/{project_id}/search",
            json={
                "query": query,
                "top_k": top_k
            },
            timeout=30
        )

        if response.status_code == 200:
            results = response.json()

            # API returns list directly, not wrapped in {"results": [...]}
            if isinstance(results, list) and len(results) > 0:
                logger.success(f"Found {len(results)} results\n")

                for i, result in enumerate(results, 1):
                    score = result.get('score', 0)
                    text = result.get('text', '')
                    metadata = result.get('metadata', {})

                    logger.info(f"   [{i}] Score: {score:.3f}")
                    logger.info(f"       Source: {metadata.get('filename', 'Unknown')}")
                    logger.info(f"       Category: {metadata.get('category', 'Unknown')}")
                    logger.info(f"       Text: {text[:150]}...")
                    logger.info("")
            else:
                logger.warning("No results found")

        elif response.status_code == 404:
            logger.error(f"❌ Project not found: {project_id}")
        else:
            logger.error(f"❌ Search failed: {response.status_code}")
            logger.error(f"   Response: {response.text}")

    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Cannot connect to MemVid API at {api_url}")
        logger.error("   Make sure MemVid containers are running")
    except Exception as e:
        logger.error(f"❌ Error during search: {e}")

def main():
    logger.info("=" * 80)
    logger.info("MEMVID SEARCH TEST - DOWNTO40 DOCUMENTATION")
    logger.info("=" * 80)

    # Load configuration
    config = load_project_config()
    api_url = config['api_url']
    project_id = config['project_id']

    logger.info(f"\n📦 Project: {config['project_name']}")
    logger.info(f"   ID: {project_id}")
    logger.info(f"   API: {api_url}")
    logger.info(f"   Documents: {config['files_uploaded']}")

    # Test queries
    test_queries = [
        "D'où viennent les 27.93 TWh exportés?",
        "Combien de dates ont été scrappées pour Generation?",
        "Quelle est la méthodologie de scraping ENTSO-E?",
        "Comment obtenir les données CO2 d'Electricity Maps?",
        "Quel est le business model de DownTo40?"
    ]

    logger.info("\n" + "=" * 80)
    logger.info("RUNNING TEST QUERIES")
    logger.info("=" * 80)

    for query in test_queries:
        test_search(api_url, project_id, query, top_k=3)
        logger.info("-" * 80)

    logger.info("\n" + "=" * 80)
    logger.info("✅ TEST COMPLETE")
    logger.info("=" * 80)
    logger.info(f"\n💡 To use in Streamlit:")
    logger.info(f"   1. Navigate to: http://localhost:8502")
    logger.info(f"   2. Select: 💬 Chat Documentation")
    logger.info(f"   3. Ask questions to the MemVid RAG system")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"\n❌ Fatal error: {e}")
        sys.exit(1)
