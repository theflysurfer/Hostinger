"""
Script 41: Fetch Carbon Intensity Data from Electricity Maps API
Downloads hourly CO2 data for France 2024 using API
Usage: python scripts/41_fetch_electricitymaps_api.py --api-key YOUR_API_KEY
"""

import requests
import pandas as pd
from pathlib import Path
from loguru import logger
import sys
import argparse
from datetime import datetime, timedelta

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

# API Configuration
API_BASE_URL = "https://api.electricitymaps.com/v3/carbon-intensity/past-range"
ZONE = "FR"  # France

def fetch_carbon_intensity(api_key, start_date, end_date):
    """Fetch carbon intensity data from Electricity Maps API"""

    logger.info(f"Fetching data from {start_date} to {end_date}...")

    params = {
        "zone": ZONE,
        "start": start_date,
        "end": end_date
    }

    headers = {
        "auth-token": api_key
    }

    try:
        response = requests.get(API_BASE_URL, params=params, headers=headers, timeout=60)

        if response.status_code == 200:
            data = response.json()
            logger.success(f"   Received {len(data.get('data', []))} records")
            return data.get('data', [])
        elif response.status_code == 401:
            logger.error("   Authentication failed. Check your API key.")
            return None
        elif response.status_code == 429:
            logger.warning("   Rate limit exceeded. Waiting 60 seconds...")
            return None
        else:
            logger.error(f"   API error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        logger.error("   Request timeout. API might be slow.")
        return None
    except Exception as e:
        logger.error(f"   Error: {e}")
        return None

def fetch_year_data(api_key, year=2024):
    """Fetch full year data in 10-day chunks (API limit)"""

    all_data = []

    # Generate all 10-day periods for the year
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)

    current = start_date
    chunk_num = 0
    total_chunks = 37  # ~366 days / 10 days

    while current < end_date:
        chunk_num += 1
        chunk_end = min(current + timedelta(days=10), end_date)

        start_str = current.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = chunk_end.strftime("%Y-%m-%dT%H:%M:%SZ")

        logger.info(f"\nChunk {chunk_num}/{total_chunks}: {current.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}")

        data = fetch_carbon_intensity(api_key, start_str, end_str)

        if data is None:
            logger.warning(f"   Failed to fetch chunk {chunk_num}")
            current = chunk_end + timedelta(seconds=1)
            continue

        all_data.extend(data)

        # Move to next chunk
        current = chunk_end + timedelta(seconds=1)

        # Rate limiting: wait between requests
        if current < end_date:
            import time
            time.sleep(2)  # 2 seconds between requests

    return all_data

def parse_api_response(data):
    """Parse API response into DataFrame"""

    if not data:
        logger.error("No data to parse")
        return None

    logger.info(f"\nParsing {len(data)} records...")

    # Extract relevant fields
    records = []
    for record in data:
        # Handle different possible field names
        carbon_intensity = record.get('carbonIntensity') or record.get('carbon_intensity')
        low_carbon_pct = record.get('fossilFreePercentage') or record.get('lowCarbonPercentage') or record.get('low_carbon_percentage')
        renewable_pct = record.get('renewablePercentage') or record.get('renewable_percentage')

        records.append({
            'datetime': record.get('datetime'),
            'carbon_intensity': carbon_intensity,
            'low_carbon_percentage': low_carbon_pct,
            'renewable_percentage': renewable_pct
        })

    df = pd.DataFrame(records)
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Sort by datetime
    df = df.sort_values('datetime').reset_index(drop=True)

    logger.success(f"Parsed DataFrame: {len(df)} rows")
    logger.info(f"   Date range: {df['datetime'].min()} to {df['datetime'].max()}")
    logger.info(f"   Columns: {list(df.columns)}")

    return df

def save_data(df, output_path):
    """Save data to CSV"""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    logger.success(f"\nSaved to: {output_path}")
    logger.info(f"   Size: {output_path.stat().st_size / (1024**2):.2f} MB")
    logger.info(f"   Rows: {len(df):,}")

def main():
    parser = argparse.ArgumentParser(description='Fetch Electricity Maps carbon intensity data')
    parser.add_argument('--api-key', required=True, help='Electricity Maps API key')
    parser.add_argument('--year', type=int, default=2024, help='Year to fetch (default: 2024)')
    parser.add_argument('--output', default='data/raw/electricitymaps_france_2024_hourly.csv',
                       help='Output CSV file path')

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("ELECTRICITY MAPS API - CARBON INTENSITY DOWNLOADER")
    logger.info("="*80)
    logger.info(f"\nConfiguration:")
    logger.info(f"   Zone: {ZONE} (France)")
    logger.info(f"   Year: {args.year}")
    logger.info(f"   Output: {args.output}")
    logger.info(f"   API Key: {args.api_key[:8]}...")

    # Fetch data
    logger.info("\n" + "-"*80)
    logger.info("FETCHING DATA FROM API")
    logger.info("-"*80)

    data = fetch_year_data(args.api_key, args.year)

    if not data:
        logger.error("\nNo data fetched. Check API key and network connection.")
        sys.exit(1)

    # Parse
    logger.info("\n" + "-"*80)
    logger.info("PARSING DATA")
    logger.info("-"*80)

    df = parse_api_response(data)

    if df is None or len(df) == 0:
        logger.error("\nFailed to parse data.")
        sys.exit(1)

    # Summary stats
    logger.info("\n" + "-"*80)
    logger.info("DATA SUMMARY")
    logger.info("-"*80)
    logger.info(f"\nCarbon Intensity Statistics:")
    logger.info(f"   Mean: {df['carbon_intensity'].mean():.1f} gCO₂eq/kWh")
    logger.info(f"   Median: {df['carbon_intensity'].median():.1f} gCO₂eq/kWh")
    logger.info(f"   Min: {df['carbon_intensity'].min():.1f} gCO₂eq/kWh")
    logger.info(f"   Max: {df['carbon_intensity'].max():.1f} gCO₂eq/kWh")

    if 'low_carbon_percentage' in df.columns:
        logger.info(f"\nLow-Carbon Percentage:")
        logger.info(f"   Mean: {df['low_carbon_percentage'].mean():.1f}%")

    if 'renewable_percentage' in df.columns:
        logger.info(f"\nRenewable Percentage:")
        logger.info(f"   Mean: {df['renewable_percentage'].mean():.1f}%")

    # Save
    logger.info("\n" + "-"*80)
    logger.info("SAVING DATA")
    logger.info("-"*80)

    save_data(df, args.output)

    logger.info("\n" + "="*80)
    logger.info("DOWNLOAD COMPLETE")
    logger.info("="*80)
    logger.info("\nNext step:")
    logger.info("   python scripts/40_analyze_carbon_vs_prices.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"\nFatal error: {e}")
        sys.exit(1)
