"""
Script 13: Generate batch scraping instructions
Creates a comprehensive summary showing exactly what needs to be scraped
"""
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR

def generate_date_range_2024():
    """Generate all dates for 2024"""
    start = datetime(2024, 1, 1)
    end = datetime(2024, 12, 31)
    dates = []
    current = start

    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates

def get_existing_dates(file_path):
    """Get dates already scraped"""
    if not os.path.exists(file_path):
        return set()

    existing = set()
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    record = json.loads(line)
                    existing.add(record['date'])
                except:
                    pass

    return existing

def main():
    print("=" * 80)
    print("ENTSO-E 2024 SCRAPING STATUS & BATCH GENERATION")
    print("=" * 80)

    output_file = f"{RAW_DATA_DIR}/entsoe_2024_scraped.jsonl"
    all_dates = generate_date_range_2024()
    existing_dates = get_existing_dates(output_file)
    remaining_dates = [d for d in all_dates if d not in existing_dates]

    print(f"\nPROGRESS:")
    print(f"   Total dates in 2024: {len(all_dates)}")
    print(f"   Already scraped: {len(existing_dates)}")
    print(f"   Remaining: {len(remaining_dates)}")
    print(f"   Progress: {len(existing_dates)/len(all_dates)*100:.1f}%")

    if len(existing_dates) > 0:
        print(f"\nCompleted dates: {sorted(existing_dates)[:5]}..." if len(existing_dates) > 5 else f"\nCompleted: {sorted(existing_dates)}")

    if len(remaining_dates) == 0:
        print("\nALL DATES SCRAPED!")
        return

    print(f"\nNext to scrape: {remaining_dates[:10]}")

    # Generate batch file for next 100 dates
    batch_size = min(100, len(remaining_dates))
    batch_file = f"{RAW_DATA_DIR}/scraping_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(batch_file, 'w') as f:
        f.write(f"ENTSO-E 2024 Batch Scraping - {batch_size} dates\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        for i, date_str in enumerate(remaining_dates[:batch_size], 1):
            url = f"https://newtransparency.entsoe.eu/market/energyPrices?appState=%7B%22sa%22%3A%5B%22BZN%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22BZN%22%2C%22mm%22%3Afalse%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%22{date_str}%22%2C%22tz%22%3A%22CET%22%7D"
            f.write(f"{i}. {date_str}\n")
            f.write(f"   URL: {url}\n\n")

    print(f"\nBatch file created: {batch_file}")
    print(f"\nRECOMMENDATION:")
    print(f"   Claude with Playwright MCP can scrape ~10-15 dates per minute")
    print(f"   Estimated time for remaining {len(remaining_dates)} dates: {len(remaining_dates)/12:.0f}-{len(remaining_dates)/10:.0f} minutes")
    print(f"\n   Continue scraping systematically through the list!")

if __name__ == "__main__":
    main()
