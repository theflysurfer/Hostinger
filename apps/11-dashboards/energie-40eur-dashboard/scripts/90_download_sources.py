"""
Script 90: Download Official Sources for RAG
Downloads PDFs and documentation from ENTSO-E, RTE, Electricity Maps, etc.
Usage: python scripts/90_download_sources.py [--priority-only]
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from urllib.parse import urlparse

# Configuration
BASE_DIR = Path(__file__).parent.parent
SOURCES_DIR = BASE_DIR / "docs" / "sources_officielles"
METADATA_FILE = BASE_DIR / "docs" / "sources_metadata.json"

# Sources to download
SOURCES = {
    "high_priority": [
        {
            "id": "entsoe_transparency_guide",
            "title": "ENTSO-E Transparency Platform User Guide",
            "url": "https://transparency.entsoe.eu/content/static_content/Static%20content/knowledge%20base/SFTP-Transparency_Docs.html",
            "output": "entsoe/transparency_platform_user_guide.pdf",
            "type": "pdf",
            "organization": "ENTSO-E",
            "topics": ["physical_flows", "generation", "load", "methodology"],
        },
        {
            "id": "rte_bilan_2024",
            "title": "RTE Bilan Électrique 2024",
            "url": "https://assets.rte-france.com/prod/2024-02/Bilan%20electrique%202024.pdf",
            "output": "rte/bilan_electrique_2024.pdf",
            "type": "pdf",
            "organization": "RTE",
            "topics": ["production", "nuclear", "renewables", "exports", "prices"],
        },
        {
            "id": "electricity_maps_methodology",
            "title": "Electricity Maps Methodology Whitepaper",
            "url": "https://static.electricitymaps.com/methodology.pdf",
            "output": "electricity_maps/methodology_whitepaper.pdf",
            "type": "pdf",
            "organization": "Electricity Maps",
            "topics": ["carbon_intensity", "lifecycle_emissions", "methodology"],
        },
        {
            "id": "entsoe_data_guide",
            "title": "ENTSO-E Transparency Platform Data Guide",
            "url": "https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html",
            "output": "entsoe/data_guide.html",
            "type": "html",
            "organization": "ENTSO-E",
            "topics": ["api", "data_definitions", "eic_codes"],
        },
        {
            "id": "rte_flux_physiques",
            "title": "RTE - Flux Physiques Méthodologie",
            "url": "https://www.rte-france.com/eco2mix/les-flux-commerciaux-et-physiques",
            "output": "rte/flux_physiques_methodologie.html",
            "type": "html",
            "organization": "RTE",
            "topics": ["physical_flows", "commercial_flows", "exports"],
        },
    ],
    "medium_priority": [
        {
            "id": "cre_observatoire",
            "title": "CRE Observatoire Marchés Électricité",
            "url": "https://www.cre.fr/content/download/27985/file/Observatoire-marches-Q3-2024.pdf",
            "output": "cre/observatoire_marches_Q3_2024.pdf",
            "type": "pdf",
            "organization": "CRE",
            "topics": ["market_prices", "spot_market"],
        },
        {
            "id": "epex_day_ahead",
            "title": "EPEX Spot Day-Ahead Market",
            "url": "https://www.epexspot.com/en/basicspowermarket",
            "output": "epex_spot/day_ahead_market.html",
            "type": "html",
            "organization": "EPEX Spot",
            "topics": ["day_ahead", "auctions", "price_formation"],
        },
        {
            "id": "rte_panorama_renouvelables",
            "title": "RTE Panorama Électricité Renouvelable 2024",
            "url": "https://assets.rte-france.com/prod/2024-01/Panorama-electricite-renouvelable-2024.pdf",
            "output": "rte/panorama_renouvelables_2024.pdf",
            "type": "pdf",
            "organization": "RTE",
            "topics": ["wind", "solar", "hydro", "renewables"],
        },
    ],
    "low_priority": [
        {
            "id": "ppe_2024",
            "title": "PPE - Programmation Pluriannuelle Énergie",
            "url": "https://www.ecologie.gouv.fr/sites/default/files/20200422_PPE.pdf",
            "output": "ministere/ppe_2024_2030.pdf",
            "type": "pdf",
            "organization": "Ministère Transition Écologique",
            "topics": ["policy", "objectives_2030"],
        },
    ]
}


def create_directories():
    """Create directory structure"""
    for org in ["entsoe", "rte", "electricity_maps", "cre", "epex_spot", "ministere"]:
        (SOURCES_DIR / org).mkdir(parents=True, exist_ok=True)
    print(f"[OK] Directories created in {SOURCES_DIR}")


def download_file(url, output_path, timeout=30):
    """Download file with retry logic"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        print(f"   Downloading from {url}...")
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        # Save file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(response.content)

        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"   [OK] Downloaded: {file_size_mb:.2f} MB")
        return True, file_size_mb

    except requests.exceptions.RequestException as e:
        print(f"   [FAIL] Failed: {e}")
        return False, 0


def generate_metadata(sources_downloaded):
    """Generate metadata JSON file"""
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_sources": len(sources_downloaded),
        "sources": sources_downloaded
    }

    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Metadata saved to {METADATA_FILE}")


def main():
    import sys

    priority_only = "--priority-only" in sys.argv

    print("=" * 80)
    print("OFFICIAL SOURCES DOWNLOADER FOR RAG")
    print("=" * 80)
    print(f"Mode: {'HIGH PRIORITY ONLY' if priority_only else 'ALL SOURCES'}\n")

    create_directories()

    # Select sources to download
    if priority_only:
        sources_to_download = SOURCES["high_priority"]
        print(f"\n[INFO] Downloading {len(sources_to_download)} HIGH PRIORITY sources...\n")
    else:
        sources_to_download = (
            SOURCES["high_priority"] +
            SOURCES["medium_priority"] +
            SOURCES["low_priority"]
        )
        print(f"\n[INFO] Downloading {len(sources_to_download)} sources (all priorities)...\n")

    # Download
    downloaded = []
    failed = []

    for idx, source in enumerate(sources_to_download, 1):
        print(f"[{idx}/{len(sources_to_download)}] {source['title']}")

        output_path = SOURCES_DIR / source['output']

        # Check if already exists
        if output_path.exists():
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"   [SKIP] Already exists ({file_size_mb:.2f} MB)")

            downloaded.append({
                **source,
                "file_path": str(output_path.relative_to(BASE_DIR)),
                "size_mb": file_size_mb,
                "downloaded_at": datetime.fromtimestamp(output_path.stat().st_mtime).isoformat(),
                "status": "existing"
            })
            continue

        # Download
        success, size_mb = download_file(source['url'], output_path)

        if success:
            downloaded.append({
                **source,
                "file_path": str(output_path.relative_to(BASE_DIR)),
                "size_mb": size_mb,
                "downloaded_at": datetime.now().isoformat(),
                "status": "downloaded"
            })
        else:
            failed.append(source)

        # Rate limiting
        time.sleep(2)

    # Summary
    print("\n" + "=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"[OK] Success: {len(downloaded)}/{len(sources_to_download)}")
    print(f"[FAIL] Failed: {len(failed)}")

    if downloaded:
        total_size = sum(s['size_mb'] for s in downloaded)
        print(f"[INFO] Total size: {total_size:.2f} MB")

    if failed:
        print("\n[WARN] Failed sources:")
        for source in failed:
            print(f"   - {source['title']}")
            print(f"     URL: {source['url']}")

    # Generate metadata
    if downloaded:
        generate_metadata(downloaded)

    print("\n" + "=" * 80)
    print(f"[INFO] Sources directory: {SOURCES_DIR}")
    print("=" * 80)

    # Next steps
    print("\n[INFO] NEXT STEPS:")
    print("1. Convert HTML files to PDF:")
    print("   node scripts/91_convert_html_to_pdf.js")
    print("\n2. Ingest into RAGFlow:")
    print("   python scripts/92_ingest_to_ragflow.py")
    print("\n3. Test RAG queries:")
    print("   python scripts/93_test_rag_queries.py")


if __name__ == "__main__":
    main()
