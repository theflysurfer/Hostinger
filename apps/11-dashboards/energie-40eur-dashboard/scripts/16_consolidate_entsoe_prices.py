"""
Script 16: Consolidate ENTSO-E Price Data
Merges all scraped JSONL files (2022-2024) into comprehensive CSV files
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_jsonl(file_path):
    """Load JSONL file and return DataFrame"""
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                records.append(record)
            except:
                continue
    return pd.DataFrame(records)

def parse_timerange(timerange_str):
    """
    Parse timerange string like '04/01/2024 00:00 - 04/01/2024 01:00'
    Returns start datetime
    """
    try:
        start_part = timerange_str.split(' - ')[0]
        return datetime.strptime(start_part, '%d/%m/%Y %H:%M')
    except:
        return None

def main():
    print('=' * 80)
    print('ENTSO-E PRICE DATA CONSOLIDATION')
    print('=' * 80)
    print()

    data_dir = Path('data/raw')
    output_dir = Path('data/processed')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load all JSONL files
    all_data = []
    years = [2022, 2023, 2024]

    for year in years:
        jsonl_file = data_dir / f'entsoe_{year}_scraped.jsonl'

        if not jsonl_file.exists():
            print(f'[!] File not found: {jsonl_file}')
            continue

        print(f'[+] Loading {year} data...')
        df = load_jsonl(jsonl_file)
        print(f'   Loaded {len(df):,} records')

        all_data.append(df)

    if not all_data:
        print('[!] No data files found!')
        return

    # Merge all data
    print(f'\n[*] Merging all data...')
    full_df = pd.concat(all_data, ignore_index=True)
    print(f'   Total records: {len(full_df):,}')

    # Parse datetime
    print(f'\n[*] Parsing timestamps...')
    full_df['datetime'] = full_df['timeRange'].apply(parse_timerange)
    full_df = full_df.dropna(subset=['datetime'])

    # Add useful columns
    full_df['year'] = full_df['datetime'].dt.year
    full_df['month'] = full_df['datetime'].dt.month
    full_df['day'] = full_df['datetime'].dt.day
    full_df['hour'] = full_df['datetime'].dt.hour
    full_df['weekday'] = full_df['datetime'].dt.dayofweek  # 0=Monday, 6=Sunday
    full_df['is_weekend'] = full_df['weekday'].isin([5, 6])

    # Flag low prices
    full_df['is_below_40'] = full_df['price'] <= 40
    full_df['is_negative'] = full_df['price'] < 0

    # Sort by datetime
    full_df = full_df.sort_values('datetime').reset_index(drop=True)

    # Save full dataset
    print(f'\n[*] Saving consolidated data...')

    # CSV with all data
    output_csv = output_dir / 'entsoe_2022_2024_prices_full.csv'
    full_df.to_csv(output_csv, index=False)
    print(f'   Full dataset: {output_csv}')
    print(f'   Records: {len(full_df):,}')

    # Summary statistics
    print(f'\n[*] Generating summary statistics...')

    summary_data = []

    for year in years:
        year_df = full_df[full_df['year'] == year]

        if len(year_df) == 0:
            continue

        total_hours = len(year_df)
        below_40_hours = year_df['is_below_40'].sum()
        negative_hours = year_df['is_negative'].sum()

        summary_data.append({
            'year': year,
            'total_hours': total_hours,
            'hours_below_40': below_40_hours,
            'percent_below_40': (below_40_hours / total_hours * 100) if total_hours > 0 else 0,
            'hours_negative': negative_hours,
            'percent_negative': (negative_hours / total_hours * 100) if total_hours > 0 else 0,
            'avg_price': year_df['price'].mean(),
            'min_price': year_df['price'].min(),
            'max_price': year_df['price'].max(),
            'median_price': year_df['price'].median()
        })

    summary_df = pd.DataFrame(summary_data)
    summary_csv = output_dir / 'entsoe_2022_2024_summary.csv'
    summary_df.to_csv(summary_csv, index=False)
    print(f'   Summary: {summary_csv}')

    # Monthly breakdown
    print(f'\n[*] Generating monthly breakdown...')
    monthly_df = full_df.groupby(['year', 'month']).agg({
        'price': ['mean', 'min', 'max', 'median'],
        'is_below_40': 'sum',
        'is_negative': 'sum',
        'datetime': 'count'
    }).reset_index()

    monthly_df.columns = ['year', 'month', 'avg_price', 'min_price', 'max_price', 'median_price',
                           'hours_below_40', 'hours_negative', 'total_hours']
    monthly_df['percent_below_40'] = (monthly_df['hours_below_40'] / monthly_df['total_hours'] * 100)

    monthly_csv = output_dir / 'entsoe_2022_2024_monthly.csv'
    monthly_df.to_csv(monthly_csv, index=False)
    print(f'   Monthly breakdown: {monthly_csv}')

    # Below 40 EUR/MWh analysis
    print(f'\n[*] Analyzing prices <=40EUR/MWh...')
    below_40_df = full_df[full_df['is_below_40']].copy()

    if len(below_40_df) > 0:
        below_40_csv = output_dir / 'entsoe_2022_2024_below_40.csv'
        below_40_df.to_csv(below_40_csv, index=False)
        print(f'   Low price hours: {below_40_csv}')
        print(f'   Records: {len(below_40_df):,}')

    # Print summary report
    print(f'\n' + '=' * 80)
    print('SUMMARY REPORT')
    print('=' * 80)

    for _, row in summary_df.iterrows():
        print(f'\n{int(row["year"])}:')
        print(f'  Total hours: {int(row["total_hours"]):,}')
        print(f'  Hours <=40EUR/MWh: {int(row["hours_below_40"]):,} ({row["percent_below_40"]:.1f}%)')
        print(f'  Hours <0EUR/MWh: {int(row["hours_negative"]):,} ({row["percent_negative"]:.1f}%)')
        print(f'  Average price: {row["avg_price"]:.2f} EUR/MWh')
        print(f'  Price range: {row["min_price"]:.2f} to {row["max_price"]:.2f} EUR/MWh')

    total_below_40 = summary_df['hours_below_40'].sum()
    total_hours = summary_df['total_hours'].sum()

    print(f'\n' + '=' * 80)
    print(f'TOTAL 2022-2024:')
    print(f'  Total hours: {int(total_hours):,}')
    print(f'  Hours <=40EUR/MWh: {int(total_below_40):,} ({total_below_40/total_hours*100:.1f}%)')
    print(f'  Average price: {full_df["price"].mean():.2f} EUR/MWh')
    print('=' * 80)

    print(f'\n[+] Consolidation complete!')
    print(f'\nOutput files saved to: {output_dir}/')

if __name__ == '__main__':
    main()
