"""
Script 11: Automated ENTSO-E 2024 Scraper with Playwright Python
Scrapes ALL 366 days of 2024 automatically
"""
import sys
import os
import json
import time
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

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

def scrape_date(page, date_str):
    """Scrape data for a single date"""
    # Construct URL with date
    url = f"https://newtransparency.entsoe.eu/market/energyPrices?appState=%7B%22sa%22%3A%5B%22BZN%7C10YFR-RTE------C%22%5D%2C%22st%22%3A%22BZN%22%2C%22mm%22%3Afalse%2C%22ma%22%3Afalse%2C%22sp%22%3A%22HALF%22%2C%22dt%22%3A%22TABLE%22%2C%22df%22%3A%22{date_str}%22%2C%22tz%22%3A%22CET%22%7D"

    try:
        # Navigate to page
        page.goto(url, timeout=30000)

        # Wait for table to load
        page.wait_for_timeout(4000)

        # Extract data using JavaScript
        data = page.evaluate("""
            () => {
                const rows = document.querySelectorAll('table tbody tr');
                const data = [];
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const timeRange = cells[0]?.textContent?.trim();
                        const priceText = cells[1]?.textContent?.trim();
                        if (timeRange && priceText && timeRange.includes('/')) {
                            const price = parseFloat(priceText.replace(/["']/g, ''));
                            data.push({
                                timeRange: timeRange,
                                price: price
                            });
                        }
                    }
                });
                return data;
            }
        """)

        if not data or len(data) == 0:
            print(f"  ⚠️  No data found for {date_str}")
            return None

        # Add date to each record
        for record in data:
            record['date'] = date_str

        return data

    except Exception as e:
        print(f"  ❌ Error scraping {date_str}: {e}")
        return None

def main():
    """Main scraping function"""
    print("=" * 80)
    print("AUTOMATED ENTSO-E 2024 SCRAPING - 366 DAYS")
    print("=" * 80)

    # Check existing data
    output_file = f"{RAW_DATA_DIR}/entsoe_2024_scraped.jsonl"
    existing_dates = set()

    if os.path.exists(output_file):
        print(f"\n[i] Found existing file: {output_file}")
        with open(output_file, 'r') as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    existing_dates.add(record['date'])
        print(f"[i] Already scraped: {len(existing_dates)} dates")

    # Generate all dates
    all_dates = generate_date_range_2024()
    dates_to_scrape = [d for d in all_dates if d not in existing_dates]

    print(f"\n[+] Total dates: {len(all_dates)}")
    print(f"[+] Already scraped: {len(existing_dates)}")
    print(f"[+] Remaining: {len(dates_to_scrape)}")
    print()

    if len(dates_to_scrape) == 0:
        print("✅ All dates already scraped!")
        return

    print(f"[+] Starting scraping from: {dates_to_scrape[0]}")
    print(f"[+] Estimated time: ~{len(dates_to_scrape) * 5 / 60:.1f} minutes")
    print()

    # Start Playwright
    with sync_playwright() as p:
        print("[+] Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        scraped_count = 0
        error_count = 0

        # Open file for appending
        with open(output_file, 'a') as f:
            for i, date_str in enumerate(dates_to_scrape, 1):
                print(f"[{i}/{len(dates_to_scrape)}] Scraping {date_str}...", end=" ")

                # Scrape date
                data = scrape_date(page, date_str)

                if data:
                    # Write to file
                    for record in data:
                        f.write(json.dumps(record) + '\n')

                    hours_below_40 = sum(1 for r in data if r['price'] <= 40)
                    print(f"✓ {len(data)} hours ({hours_below_40} ≤40€)")
                    scraped_count += 1

                    # Flush every 10 dates
                    if i % 10 == 0:
                        f.flush()
                        print(f"    💾 Progress saved ({scraped_count}/{len(dates_to_scrape)})")
                else:
                    error_count += 1

                # Rate limiting
                time.sleep(2)

                # Progress checkpoint every 50 dates
                if i % 50 == 0:
                    print()
                    print(f"📊 Progress: {i}/{len(dates_to_scrape)} ({i/len(dates_to_scrape)*100:.1f}%)")
                    print(f"   Scraped: {scraped_count}, Errors: {error_count}")
                    print()

        browser.close()

    print()
    print("=" * 80)
    print("✅ SCRAPING COMPLETE!")
    print("=" * 80)
    print(f"Successfully scraped: {scraped_count} dates")
    print(f"Errors: {error_count} dates")
    print(f"Output file: {output_file}")

    # Count total records
    total_records = 0
    with open(output_file, 'r') as f:
        for line in f:
            if line.strip():
                total_records += 1

    print(f"Total hourly records: {total_records}")
    print(f"Expected: {len(all_dates) * 24} (366 days × 24 hours)")

if __name__ == "__main__":
    main()
