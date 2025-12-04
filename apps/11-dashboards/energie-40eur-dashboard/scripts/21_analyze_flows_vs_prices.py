"""
Script 21: Analyze Physical Flows vs Prices
Crosses exported flows with spot prices to answer: How many MWh exported at ≤40€?
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
FLOWS_FILE = BASE_DIR / "data" / "raw" / "entsoe_flows_2024_scraped.jsonl"
PRICES_FILE = BASE_DIR / "data" / "processed" / "entsoe_2022_2024_prices_full.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "flows_vs_prices_2024.csv"

def parse_time_range(time_range):
    """Convert '00:00 - 01:00' to hour index 0-23"""
    start_time = time_range.split(' - ')[0]
    hour = int(start_time.split(':')[0])
    return hour

def load_flows_data():
    """Load and parse JSONL flows data"""
    print("[+] Loading Physical Flows data...")

    records = []
    with open(FLOWS_FILE, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)

                # Parse date and hour
                date = data['date']
                hour = parse_time_range(data['timeRange'])
                timestamp = f"{date} {hour:02d}:00"

                # Calculate net exports (FR→X minus X→FR)
                flows = data['flows']
                net_be = flows['FR-BE'] - flows['BE-FR']
                net_de = flows['FR-DE'] - flows['DE-FR']
                net_it = flows['FR-IT'] - flows['IT-FR']
                net_es = flows['FR-ES'] - flows['ES-FR']
                net_ch = flows['FR-CH'] - flows['CH-FR']
                net_uk = flows['FR-UK'] - flows['UK-FR']

                total_net = net_be + net_de + net_it + net_es + net_ch + net_uk

                records.append({
                    'timestamp': timestamp,
                    'date': date,
                    'hour': hour,
                    'net_be_mw': net_be,
                    'net_de_mw': net_de,
                    'net_it_mw': net_it,
                    'net_es_mw': net_es,
                    'net_ch_mw': net_ch,
                    'net_uk_mw': net_uk,
                    'total_net_exports_mw': total_net
                })

            except Exception as e:
                print(f"[!] Line {line_num}: {e}")
                continue

    df = pd.DataFrame(records)
    print(f"[OK] Loaded {len(df)} hourly flow records")
    print(f"     Date range: {df['date'].min()} -> {df['date'].max()}")

    return df

def load_prices_data():
    """Load spot prices data"""
    print("\n[+] Loading Spot Prices data...")

    df = pd.read_csv(PRICES_FILE)

    # Create timestamp for merging (datetime column already exists)
    df['timestamp'] = df['date'] + ' ' + df['hour'].apply(lambda h: f"{h:02d}:00")

    print(f"[OK] Loaded {len(df)} hourly price records")
    print(f"     Date range: {df['date'].min()} -> {df['date'].max()}")

    # Filter only 2024 data
    df_2024 = df[df['year'] == 2024].copy()
    print(f"[OK] Filtered to {len(df_2024)} records for 2024")

    return df_2024[['timestamp', 'date', 'hour', 'price']].rename(columns={'price': 'Price_EUR_MWh', 'date': 'Date', 'hour': 'Hour'})

def analyze():
    """Main analysis"""
    print("="*80)
    print("PHYSICAL FLOWS vs SPOT PRICES ANALYSIS (2024)")
    print("="*80)

    # Load data
    flows_df = load_flows_data()
    prices_df = load_prices_data()

    # Merge
    print("\n[+] Merging flows + prices...")
    merged = pd.merge(
        flows_df,
        prices_df,
        on='timestamp',
        how='inner'
    )

    print(f"[OK] Merged {len(merged)} hourly records")

    # Save merged data
    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"[SAVE] Saved to: {OUTPUT_FILE}")

    # Analysis
    print("\n" + "="*80)
    print("EXPORTS ANALYSIS BY PRICE THRESHOLD")
    print("="*80)

    # Filter exports only (positive net exports)
    exports = merged[merged['total_net_exports_mw'] > 0].copy()

    # Price thresholds
    thresholds = [0, 10, 20, 30, 40, 50]

    print(f"\n{'Threshold':<12} {'Hours':<8} {'Avg Export (GW)':<18} {'Total Volume (TWh)':<20} {'% of Year'}")
    print("-"*80)

    for threshold in thresholds:
        subset = exports[exports['Price_EUR_MWh'] <= threshold]

        hours = len(subset)
        avg_export_gw = subset['total_net_exports_mw'].mean() / 1000 if hours > 0 else 0
        total_twh = subset['total_net_exports_mw'].sum() / 1_000_000 if hours > 0 else 0
        pct_year = (hours / 8760 * 100) if hours > 0 else 0

        print(f"<={threshold:3d} EUR/MWh    {hours:5d}h   {avg_export_gw:7.2f} GW        {total_twh:8.2f} TWh         {pct_year:5.1f}%")

    # Breakdown by country for <=40 EUR
    print("\n" + "="*80)
    print("EXPORTS BY COUNTRY DURING HOURS <=40 EUR/MWh")
    print("="*80)

    subset_40 = exports[exports['Price_EUR_MWh'] <= 40]

    countries = [
        ('Belgium', 'net_be_mw'),
        ('Germany', 'net_de_mw'),
        ('Italy', 'net_it_mw'),
        ('Spain', 'net_es_mw'),
        ('Switzerland', 'net_ch_mw'),
        ('UK', 'net_uk_mw')
    ]

    print(f"\n{'Country':<15} {'Avg Export (MW)':<18} {'Total Volume (TWh)':<20} {'% of Total Exports'}")
    print("-"*80)

    total_exports_40 = subset_40['total_net_exports_mw'].sum()

    for country, col in countries:
        # Only positive flows (exports)
        country_exports = subset_40[subset_40[col] > 0][col]

        avg_mw = country_exports.mean() if len(country_exports) > 0 else 0
        total_twh = country_exports.sum() / 1_000_000 if len(country_exports) > 0 else 0
        pct_total = (country_exports.sum() / total_exports_40 * 100) if total_exports_40 > 0 else 0

        print(f"{country:<15} {avg_mw:8.0f} MW        {total_twh:8.2f} TWh         {pct_total:6.1f}%")

    # Negative prices analysis
    print("\n" + "="*80)
    print("EXPORTS DURING NEGATIVE PRICES")
    print("="*80)

    negative = exports[exports['Price_EUR_MWh'] < 0]

    if len(negative) > 0:
        hours_neg = len(negative)
        avg_export_neg = negative['total_net_exports_mw'].mean() / 1000
        total_neg_twh = negative['total_net_exports_mw'].sum() / 1_000_000
        avg_price_neg = negative['Price_EUR_MWh'].mean()

        print(f"\nHours with negative prices: {hours_neg}h ({hours_neg/8760*100:.1f}% of year)")
        print(f"Average export during negative prices: {avg_export_neg:.2f} GW")
        print(f"Total volume exported at negative prices: {total_neg_twh:.2f} TWh")
        print(f"Average negative price: {avg_price_neg:.2f} €/MWh")
        print(f"\n[!] Economic loss: {total_neg_twh * abs(avg_price_neg):.1f} M EUR (if paid at negative price)")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY: BUSINESS OPPORTUNITY")
    print("="*80)

    hours_40 = len(subset_40)
    total_40_twh = subset_40['total_net_exports_mw'].sum() / 1_000_000
    avg_price_40 = subset_40['Price_EUR_MWh'].mean()

    print(f"\nHours at <=40 EUR/MWh: {hours_40}h ({hours_40/8760*100:.1f}% of 2024)")
    print(f"Total exports during these hours: {total_40_twh:.2f} TWh")
    print(f"Average price during these hours: {avg_price_40:.2f} EUR/MWh")
    print(f"\n[*] VALORISATION POTENTIAL:")
    print(f"   If we could capture 10% of these exports:")
    print(f"   Volume: {total_40_twh * 0.1:.2f} TWh")
    print(f"   Buy at: ~{avg_price_40:.0f} EUR/MWh")
    print(f"   Sell at: 40 EUR/MWh")
    print(f"   Margin: ~{40 - avg_price_40:.0f} EUR/MWh")
    print(f"   Revenue: {total_40_twh * 0.1 * (40 - avg_price_40):.1f} M EUR/year")

    print("\n" + "="*80)
    print(f"[OK] Analysis complete! Results saved to: {OUTPUT_FILE}")
    print("="*80)

if __name__ == "__main__":
    analyze()
