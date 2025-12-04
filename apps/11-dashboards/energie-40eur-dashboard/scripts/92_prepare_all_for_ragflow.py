"""
Script 92: Prepare ALL Sources for RAGFlow Ingestion
Creates a comprehensive RAG-ready package with all docs, screenshots, and metadata
Usage: python scripts/92_prepare_all_for_ragflow.py
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import base64

# Configuration
BASE_DIR = Path(__file__).parent.parent
RAG_PACKAGE_DIR = BASE_DIR / "data" / "rag_package"
OUTPUT_MANIFEST = RAG_PACKAGE_DIR / "ingestion_manifest.json"

# Define all sources to include
SOURCES_INVENTORY = {
    "documentation": {
        "description": "Project documentation and analysis reports",
        "files": [
            "docs/BUSINESS_MODEL_VALIDATION.md",
            "docs/SPRINT1_RESULTS_SUMMARY.md",
            "docs/SPRINT2_RESULTS_SUMMARY.md",
            "docs/SCRAPING_ACTION_PLAN.md",
            "docs/SCRAPING_SUMMARY.md",
            "docs/VALIDATION_DATA_SOURCES.md",
            "docs/ENTSOE_DATA_SOURCES.md",
            "docs/ELECTRICITY_MAPS_EXPLORATION.md",
            "docs/METHODOLOGY_SOURCES_ILLUSTRATION.md",
            "docs/SOURCES_TO_DOWNLOAD.md",
            "docs/DEPLOYMENT_PLAN.md",
        ]
    },
    "official_sources": {
        "description": "Downloaded official documentation (ENTSO-E, RTE, etc.)",
        "files": [
            "docs/sources_officielles/entsoe/transparency_platform_user_guide.pdf",
            "docs/sources_officielles/entsoe/data_guide.html",
        ]
    },
    "screenshots": {
        "description": "Visual evidence from source platforms",
        "files": [
            ".playwright-mcp/electricitymaps_france_current.png",
            ".playwright-mcp/electricitymaps_france_datasets.png",
            ".playwright-mcp/entsoe_energy_prices_page.png",
            ".playwright-mcp/entsoe_france_energy_prices.png",
            ".playwright-mcp/entsoe_physical_flows.png",
            ".playwright-mcp/generation_france_table.png",
        ]
    },
    "metadata": {
        "description": "Scraping results and backlog tracking",
        "files": [
            "data/backlog/failed_scraping_dates.json",
            "docs/sources_metadata.json",
        ]
    },
    "scripts": {
        "description": "Key scraping and analysis scripts for methodology reference",
        "files": [
            "scripts/20_scrape_physical_flows.js",
            "scripts/22_scrape_generation.js",
            "scripts/30_scrape_load.js",
        ]
    }
}


def create_rag_package():
    """Create RAG package directory structure"""
    RAG_PACKAGE_DIR.mkdir(parents=True, exist_ok=True)

    for category in SOURCES_INVENTORY.keys():
        (RAG_PACKAGE_DIR / category).mkdir(exist_ok=True)

    print(f"[OK] Created RAG package directory: {RAG_PACKAGE_DIR}")


def copy_file_to_rag(source_path, category):
    """Copy file to RAG package and return metadata"""
    source = BASE_DIR / source_path

    if not source.exists():
        print(f"   [SKIP] File not found: {source_path}")
        return None

    # Determine destination
    filename = source.name
    dest = RAG_PACKAGE_DIR / category / filename

    # Copy file
    shutil.copy2(source, dest)

    # Get file info
    file_size = source.stat().st_size
    file_size_mb = file_size / (1024 * 1024)

    # Create metadata
    metadata = {
        "filename": filename,
        "original_path": str(source_path),
        "rag_path": str(dest.relative_to(BASE_DIR)),
        "category": category,
        "size_bytes": file_size,
        "size_mb": round(file_size_mb, 2),
        "extension": source.suffix,
        "modified_at": datetime.fromtimestamp(source.stat().st_mtime).isoformat(),
        "copied_at": datetime.now().isoformat(),
    }

    # Add type-specific metadata
    if source.suffix == '.md':
        # Count lines for markdown
        with open(source, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            metadata["lines"] = len(lines)
            metadata["type"] = "markdown"

    elif source.suffix == '.json':
        # Validate JSON
        try:
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)
                metadata["type"] = "json"
                metadata["json_valid"] = True
        except:
            metadata["type"] = "json"
            metadata["json_valid"] = False

    elif source.suffix in ['.png', '.jpg', '.jpeg']:
        metadata["type"] = "image"
        # For RAGFlow, we'll need to convert images to text descriptions later

    elif source.suffix == '.pdf':
        metadata["type"] = "pdf"

    elif source.suffix == '.html':
        metadata["type"] = "html"

    elif source.suffix == '.js':
        metadata["type"] = "javascript"
        with open(source, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            metadata["lines"] = len(lines)

    print(f"   [OK] Copied: {filename} ({file_size_mb:.2f} MB)")
    return metadata


def generate_screenshot_descriptions():
    """Generate text descriptions for screenshots for RAG ingestion"""
    descriptions = {
        "electricitymaps_france_current.png": {
            "title": "Electricity Maps France Real-Time Dashboard",
            "date": "2025-10-27",
            "content": """
            Screenshot of Electricity Maps showing France real-time electricity data:
            - Carbon intensity: 12 gCO2eq/kWh
            - Low carbon: 100%
            - Renewable: 39%
            - Real-time mix breakdown by generation source
            - Price data available
            Source: https://app.electricitymaps.com/map/zone/FR/live
            """
        },
        "electricitymaps_france_datasets.png": {
            "title": "Electricity Maps France 2024 Datasets Discovery",
            "date": "2025-10-27",
            "content": """
            Screenshot proving availability of FREE CSV datasets from Electricity Maps:
            - Zone: FR (France)
            - Year: 2024 available
            - Granularities: Hourly (8,784 hours), 5-min, 15-min, daily, monthly
            - Signals: Carbon intensity, Carbon-free %, Renewable %
            - Access: Free account required
            - Format: CSV downloadable
            - Eliminates need for 3-4 days of scraping work
            Source: https://app.electricitymaps.com/datasets?zone=FR
            """
        },
        "entsoe_physical_flows.png": {
            "title": "ENTSO-E Physical Flows France 2024 Data Table",
            "date": "2025-10-27",
            "content": """
            Screenshot of ENTSO-E Transparency Platform showing Physical Flows for France:
            - Date shown: 2024-06-15
            - Bidding Zone: FR (10YFR-RTE------C)
            - Shows hourly cross-border electricity flows
            - Imports and exports to neighboring countries
            - Used to scrape 348/366 dates (95.1% success)
            - Total: 27.93 TWh exported at <=40€/MWh validated from this data
            Source: https://newtransparency.entsoe.eu/transmission-domain/physicalFlow
            """
        },
        "generation_france_table.png": {
            "title": "ENTSO-E Generation by Production Type France 2024",
            "date": "2025-10-27",
            "content": """
            Screenshot of ENTSO-E showing electricity generation breakdown:
            - Date: 2024-06-15
            - 21 production types captured (Nuclear, Wind, Solar, Hydro, Fossil)
            - Hourly granularity (00:00-01:00 example shown)
            - Nuclear: 35,644 MW (62% of mix)
            - Wind Onshore: 7,989 MW (14%)
            - Used to scrape 360/366 dates (98.4% success) = 8,640 hours
            Source: https://newtransparency.entsoe.eu/generation/actual/perType/generation
            """
        },
        "entsoe_france_energy_prices.png": {
            "title": "ENTSO-E France Day-Ahead Prices 2024",
            "date": "2025-10-27",
            "content": """
            Screenshot of ENTSO-E day-ahead electricity prices for France:
            - Shows hourly spot prices
            - Used to validate low price hours (<=40€/MWh)
            - 3,012 hours identified at <=40€ (34.3% of year 2024)
            Source: https://newtransparency.entsoe.eu/market/day-ahead-prices
            """
        },
        "entsoe_energy_prices_page.png": {
            "title": "ENTSO-E Day-Ahead Prices Interface Overview",
            "date": "2025-10-27",
            "content": """
            Screenshot of ENTSO-E Transparency Platform Day-Ahead Prices section:
            - Interface for accessing European electricity spot prices
            - Allows zone selection (France: FR)
            - Date range selection
            - Export capabilities
            Source: https://newtransparency.entsoe.eu/market/day-ahead-prices
            """
        }
    }

    # Write descriptions as JSON for RAGFlow
    desc_file = RAG_PACKAGE_DIR / "screenshots" / "screenshot_descriptions.json"
    with open(desc_file, 'w', encoding='utf-8') as f:
        json.dump(descriptions, f, indent=2, ensure_ascii=False)

    print(f"[OK] Generated screenshot descriptions: {desc_file.name}")
    return descriptions


def create_master_context_doc():
    """Create a master context document for RAG"""
    context = f"""
# DownTo40 Project - Master Context Document

**Generated**: {datetime.now().isoformat()}
**Purpose**: Provide comprehensive context for RAG queries about project data sources and methodology

---

## Project Overview

**DownTo40** is a data-driven analysis of French electricity markets, focusing on the economic opportunity
of consuming electricity during low-price hours (<=40€/MWh in 2024).

**Key Finding**:
- 3,012 hours (34.3% of 2024) had spot prices <=40€/MWh
- 27.93 TWh were exported during these low-price hours
- Represents significant untapped flexibility potential

---

## Data Sources

### 1. ENTSO-E Transparency Platform
- **Physical Flows**: Cross-border electricity exchanges
  - Scraped: 348/366 dates (95.1%)
  - Validated: 27.93 TWh exports at <=40€

- **Generation by Type**: Electricity production breakdown (21 sources)
  - Scraped: 360/366 dates (98.4%)
  - Data: 8,640 hours of detailed generation
  - Types: Nuclear, Wind (onshore/offshore), Solar, Hydro, Fossil, etc.

- **Actual Total Load**: Electricity consumption
  - Scraping: In progress
  - Target: 366 dates for 2024

### 2. RTE ODRÉ (Open Data Réseaux Énergies)
- **Day-Ahead Spot Prices**: French electricity market prices
  - Source: EPEX Spot market
  - Granularity: Hourly
  - Used to identify: 3,012 hours at <=40€/MWh

### 3. Electricity Maps
- **Carbon Intensity**: gCO2eq/kWh of consumed electricity
  - Method: Discovered FREE CSV datasets (no scraping needed!)
  - Granularity: Hourly for 2024 (8,784 hours)
  - Signals: Carbon intensity, Low carbon %, Renewable %
  - Access: Free account at https://app.electricitymaps.com/datasets

---

## Scraping Methodology

All scraping performed using **Playwright** (headless browser automation):

1. **Incremental Approach**: Skip already-scraped dates for crash resilience
2. **JSONL Format**: One JSON record per line for fault tolerance
3. **Rate Limiting**: 3s delay between requests
4. **Timeout Handling**: 30s default (increased to 45-60s for retries)
5. **Backlog Tracking**: Failed dates logged in `data/backlog/failed_scraping_dates.json`

**Success Rates**:
- Physical Flows: 95.1% (348/366)
- Generation: 98.4% (360/366)
- Load: In progress

---

## Business Model

**Target Clients**: Industrial electricity consumers (data centers, factories, electrolyzers)

**Value Proposition**:
1. **Cost Savings**: Shift consumption to <=40€ hours → 60% savings vs average
2. **Green Energy**: Low-price hours correlate with high renewable production
3. **Grid Services**: Flexibility = additional revenue streams

**Revenue Model**:
- Subscription: €X/month per MW of flexible capacity
- Performance-based: % of realized savings

---

## Documentation Structure

- `BUSINESS_MODEL_VALIDATION.md`: Economic analysis and market validation
- `SPRINT1_RESULTS_SUMMARY.md`: Physical Flows scraping results
- `SPRINT2_RESULTS_SUMMARY.md`: Generation scraping results
- `SCRAPING_ACTION_PLAN.md`: Complete scraping methodology
- `ELECTRICITY_MAPS_EXPLORATION.md`: CO2 data strategy
- `METHODOLOGY_SOURCES_ILLUSTRATION.md`: Traceability proposals

---

## Key Metrics

**Market Opportunity (2024)**:
- Low-price hours: 3,012h (34.3%)
- Export volume @ <=40€: 27.93 TWh
- Average price @ <=40€: ~25€/MWh
- Average price overall: ~65€/MWh
- Potential savings: ~40€/MWh × flexible consumption

**Data Coverage**:
- Prices: 100% (RTE ODRÉ complete dataset)
- Physical Flows: 95.1% (348/366 dates)
- Generation: 98.4% (360/366 dates)
- Load: In progress
- Carbon Intensity: To be downloaded (FREE CSV available)

---

## Technical Stack

**Data Collection**:
- Playwright (Node.js) for web scraping
- Python for data processing and analysis

**Data Storage**:
- Raw: JSONL files (crash-resistant)
- Processed: CSV for analysis
- Database: TBD (PostgreSQL or TimescaleDB)

**Analysis & Visualization**:
- Python: pandas, numpy, matplotlib
- Dashboard: Streamlit
- RAG: RAGFlow for document Q&A

**Deployment**:
- Server: Hostinger VPS (69.62.108.82)
- Container: Docker
- Domain: energie.srv759970.hstgr.cloud

---

## Questions This RAG Can Answer

1. "Where do the 27.93 TWh exports come from?"
   → SPRINT1_RESULTS_SUMMARY.md + Physical Flows scraping

2. "What is the scraping methodology?"
   → SCRAPING_ACTION_PLAN.md + individual sprint reports

3. "How many dates were scraped successfully?"
   → Sprint summaries + failed_scraping_dates.json

4. "What production types are tracked?"
   → SPRINT2_RESULTS_SUMMARY.md (21 types listed)

5. "How is carbon intensity obtained?"
   → ELECTRICITY_MAPS_EXPLORATION.md (FREE CSV datasets)

6. "What is the business model?"
   → BUSINESS_MODEL_VALIDATION.md

7. "What are the data sources?"
   → VALIDATION_DATA_SOURCES.md + ENTSOE_DATA_SOURCES.md

---

## File Locations

All source documents are located in:
- `docs/` - Project documentation
- `docs/sources_officielles/` - Downloaded official sources
- `.playwright-mcp/` - Screenshots evidence
- `data/backlog/` - Scraping backlog tracking
- `scripts/` - Scraping and analysis scripts

---

**End of Master Context Document**
"""

    context_file = RAG_PACKAGE_DIR / "MASTER_CONTEXT.md"
    with open(context_file, 'w', encoding='utf-8') as f:
        f.write(context)

    print(f"[OK] Created master context: {context_file.name}")
    return context_file


def main():
    print("=" * 80)
    print("PREPARE ALL SOURCES FOR RAGFLOW")
    print("=" * 80)
    print()

    # Create RAG package directory
    create_rag_package()
    print()

    # Copy all files
    manifest = {
        "created_at": datetime.now().isoformat(),
        "total_files": 0,
        "total_size_mb": 0,
        "categories": {}
    }

    for category, info in SOURCES_INVENTORY.items():
        print(f"[{category.upper()}] {info['description']}")

        category_files = []
        for file_path in info['files']:
            metadata = copy_file_to_rag(file_path, category)
            if metadata:
                category_files.append(metadata)
                manifest["total_files"] += 1
                manifest["total_size_mb"] += metadata["size_mb"]

        manifest["categories"][category] = {
            "description": info["description"],
            "file_count": len(category_files),
            "files": category_files
        }
        print()

    # Generate screenshot descriptions
    print("[SCREENSHOTS] Generating text descriptions for RAG...")
    descriptions = generate_screenshot_descriptions()
    print()

    # Create master context document
    print("[CONTEXT] Creating master context document...")
    context_file = create_master_context_doc()
    print()

    # Add context to manifest
    manifest["master_context"] = str(context_file.relative_to(BASE_DIR))
    manifest["screenshot_descriptions"] = "data/rag_package/screenshots/screenshot_descriptions.json"

    # Save manifest
    with open(OUTPUT_MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Summary
    print("=" * 80)
    print("PACKAGE SUMMARY")
    print("=" * 80)
    print(f"[OK] Total files: {manifest['total_files']}")
    print(f"[OK] Total size: {manifest['total_size_mb']:.2f} MB")
    print(f"[OK] Categories: {len(manifest['categories'])}")
    print()

    for category, data in manifest["categories"].items():
        print(f"  {category}: {data['file_count']} files")

    print()
    print(f"[OK] Manifest saved: {OUTPUT_MANIFEST.relative_to(BASE_DIR)}")
    print(f"[OK] RAG package: {RAG_PACKAGE_DIR.relative_to(BASE_DIR)}")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Upload RAG package to RAGFlow:")
    print("   - Manually: Via RAGFlow UI at https://ragflow.srv759970.hstgr.cloud")
    print("   - API: python scripts/93_upload_to_ragflow.py")
    print()
    print("2. Test RAG queries:")
    print("   python scripts/94_test_rag_queries.py")
    print()
    print("3. Integrate into Streamlit dashboard:")
    print("   python streamlit_app.py (with Sources page)")


if __name__ == "__main__":
    main()
