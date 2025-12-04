"""
Script 18: Validate ENTSO-E scraped data vs GitHub open source data
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def load_github_data():
    """Load GitHub CSV data"""
    df = pd.read_csv('data/raw/epex_spot_prices_github.csv')
    df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['start_hour'])
    df['price'] = df['price_euros_mwh']
    return df[['datetime', 'price']]

def load_entso_data(year):
    """Load ENTSO-E scraped JSONL data"""
    file_path = Path(f'data/raw/entsoe_{year}_scraped.jsonl')

    if not file_path.exists():
        return None

    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                records.append(record)
            except:
                continue

    if not records:
        return None

    df = pd.DataFrame(records)

    # Parse datetime from timeRange "05/04/2024 00:00 - 05/04/2024 01:00"
    def parse_time(time_str):
        try:
            start = time_str.split(' - ')[0]
            return datetime.strptime(start, '%d/%m/%Y %H:%M')
        except:
            return None

    df['datetime'] = df['timeRange'].apply(parse_time)
    df = df.dropna(subset=['datetime'])

    return df[['datetime', 'price']]

def compare_sources(github_df, entso_df, year):
    """Compare GitHub and ENTSO-E data for overlapping period"""
    print(f'\n{"=" * 80}')
    print(f'VALIDATION {year}: GitHub vs ENTSO-E Scraping')
    print('=' * 80)

    # Find overlapping dates
    github_year = github_df[github_df['datetime'].dt.year == year].copy()
    entso_year = entso_df[entso_df['datetime'].dt.year == year].copy()

    print(f'\nGitHub data:')
    print(f'   Records: {len(github_year):,}')
    print(f'   Period: {github_year["datetime"].min()} to {github_year["datetime"].max()}')

    print(f'\nENTSO-E scraped:')
    print(f'   Records: {len(entso_year):,}')
    print(f'   Period: {entso_year["datetime"].min()} to {entso_year["datetime"].max()}')

    # Merge on datetime
    merged = pd.merge(
        github_year,
        entso_year,
        on='datetime',
        suffixes=('_github', '_entso'),
        how='inner'
    )

    if len(merged) == 0:
        print(f'\n[WARNING] No overlapping data for {year}!')
        return

    print(f'\nOverlapping records: {len(merged):,}')

    # Calculate differences
    merged['diff'] = merged['price_entso'] - merged['price_github']
    merged['diff_pct'] = (merged['diff'] / merged['price_github'] * 100).abs()

    # Statistics
    print(f'\n{"=" * 80}')
    print('COMPARISON STATISTICS')
    print('=' * 80)

    print(f'\nPrix moyens:')
    print(f'   GitHub: {merged["price_github"].mean():.2f} EUR/MWh')
    print(f'   ENTSO-E: {merged["price_entso"].mean():.2f} EUR/MWh')
    print(f'   Difference: {merged["diff"].mean():.2f} EUR/MWh')

    print(f'\nEcart absolu (EUR/MWh):')
    print(f'   Moyen: {merged["diff"].abs().mean():.2f}')
    print(f'   Median: {merged["diff"].abs().median():.2f}')
    print(f'   Max: {merged["diff"].abs().max():.2f}')
    print(f'   Min: {merged["diff"].abs().min():.2f}')

    print(f'\nEcart relatif (%):')
    print(f'   Moyen: {merged["diff_pct"].mean():.2f}%')
    print(f'   Median: {merged["diff_pct"].median():.2f}%')
    print(f'   Max: {merged["diff_pct"].max():.2f}%')

    # Quality check
    exact_match = (merged['diff'].abs() < 0.01).sum()
    close_match = (merged['diff'].abs() < 1.0).sum()
    good_match = (merged['diff_pct'] < 5.0).sum()

    print(f'\nQualite des donnees:')
    print(f'   Exact match (<0.01 EUR): {exact_match:,} ({exact_match/len(merged)*100:.1f}%)')
    print(f'   Close match (<1 EUR): {close_match:,} ({close_match/len(merged)*100:.1f}%)')
    print(f'   Good match (<5% diff): {good_match:,} ({good_match/len(merged)*100:.1f}%)')

    # Show worst mismatches
    worst = merged.nlargest(5, 'diff_pct')[['datetime', 'price_github', 'price_entso', 'diff', 'diff_pct']]

    if len(worst) > 0:
        print(f'\nTop 5 ecarts:')
        for _, row in worst.iterrows():
            print(f'   {row["datetime"]}: GitHub={row["price_github"]:.2f}EUR, '
                  f'ENTSO={row["price_entso"]:.2f}EUR, diff={row["diff"]:.2f}EUR ({row["diff_pct"]:.1f}%)')

    # Overall verdict
    print(f'\n{"=" * 80}')
    if merged["diff_pct"].median() < 1.0:
        print('[EXCELLENT] Les donnees sont quasi-identiques!')
    elif merged["diff_pct"].median() < 5.0:
        print('[BON] Les donnees sont tres coherentes')
    elif merged["diff_pct"].median() < 10.0:
        print('[MOYEN] Differences notables mais acceptables')
    else:
        print('[ATTENTION] Differences importantes detectees')

    print('=' * 80)

def main():
    print('=' * 80)
    print('VALIDATION: ENTSO-E Scraping vs GitHub Open Source')
    print('=' * 80)

    # Load GitHub data
    print('\nLoading GitHub data...')
    github_df = load_github_data()
    print(f'   Total records: {len(github_df):,}')
    print(f'   Period: {github_df["datetime"].min()} to {github_df["datetime"].max()}')

    # Compare each year
    for year in [2022, 2023, 2024]:
        entso_df = load_entso_data(year)

        if entso_df is None:
            print(f'\n[SKIP] {year}: No ENTSO-E data available')
            continue

        compare_sources(github_df, entso_df, year)

    print('\n' + '=' * 80)
    print('VALIDATION COMPLETE')
    print('=' * 80)

if __name__ == '__main__':
    main()
