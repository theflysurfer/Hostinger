"""
Script 17: Quick comparison of 2022 (partial) vs 2023 vs 2024
"""
import json
import pandas as pd
from pathlib import Path

def load_jsonl(file_path):
    """Load JSONL file"""
    records = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                records.append(record)
            except:
                continue
    return pd.DataFrame(records)

def analyze_year(df, year_label):
    """Analyze a single year"""
    total_records = len(df)
    below_40 = df[df['price'] <= 40]
    negative = df[df['price'] < 0]

    return {
        'year': year_label,
        'records': total_records,
        'hours_below_40': len(below_40),
        'pct_below_40': (len(below_40) / total_records * 100) if total_records > 0 else 0,
        'hours_negative': len(negative),
        'pct_negative': (len(negative) / total_records * 100) if total_records > 0 else 0,
        'avg_price': df['price'].mean(),
        'min_price': df['price'].min(),
        'max_price': df['price'].max(),
        'median_price': df['price'].median()
    }

def main():
    print('=' * 80)
    print('COMPARAISON RAPIDE 2022 vs 2023 vs 2024')
    print('=' * 80)
    print()

    data_dir = Path('data/raw')
    results = []

    # Load each year
    for year in [2022, 2023, 2024]:
        file_path = data_dir / f'entsoe_{year}_scraped.jsonl'

        if not file_path.exists():
            print(f'⚠️  {year}: Fichier non trouvé')
            continue

        df = load_jsonl(file_path)

        if len(df) == 0:
            print(f'⚠️  {year}: Aucune donnée')
            continue

        # Get date range for partial data
        df['date_parsed'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        date_range = f"{df['date_parsed'].min().strftime('%Y-%m-%d')} à {df['date_parsed'].max().strftime('%Y-%m-%d')}"

        stats = analyze_year(df, year)
        stats['date_range'] = date_range
        stats['days_scraped'] = df['date_parsed'].nunique()

        results.append(stats)

        print(f'\n[{year}] ({stats["days_scraped"]} jours scrapes)')
        print(f'   Periode: {date_range}')
        print(f'   Total heures: {stats["records"]:,}')
        print(f'   Heures <=40EUR: {stats["hours_below_40"]:,} ({stats["pct_below_40"]:.1f}%)')
        print(f'   Heures <0EUR: {stats["hours_negative"]:,} ({stats["pct_negative"]:.2f}%)')
        print(f'   Prix moyen: {stats["avg_price"]:.2f} EUR/MWh')
        print(f'   Prix min: {stats["min_price"]:.2f} EUR/MWh')
        print(f'   Prix max: {stats["max_price"]:.2f} EUR/MWh')

    if len(results) >= 2:
        print('\n' + '=' * 80)
        print('COMPARAISON')
        print('=' * 80)

        # Sort by year
        results_sorted = sorted(results, key=lambda x: x['year'])

        print(f'\nEvolution Prix Moyen:')
        for r in results_sorted:
            print(f'   {r["year"]}: {r["avg_price"]:.2f} EUR/MWh')

        print(f'\nHeures <=40EUR/MWh (% du total):')
        for r in results_sorted:
            status = "[EXCELLENT]" if r["pct_below_40"] > 20 else "[MOYEN]" if r["pct_below_40"] > 5 else "[FAIBLE]"
            print(f'   {r["year"]}: {r["hours_below_40"]:,} heures ({r["pct_below_40"]:.1f}%) {status}')

        print(f'\nPrix Negatifs (% du total):')
        for r in results_sorted:
            print(f'   {r["year"]}: {r["hours_negative"]:,} heures ({r["pct_negative"]:.2f}%)')

        # Find best/worst years
        best_year = max(results, key=lambda x: x['pct_below_40'])
        worst_year = min(results, key=lambda x: x['pct_below_40'])

        print(f'\n[MEILLEURE] Annee pour prix bas: {best_year["year"]} ({best_year["pct_below_40"]:.1f}%)')
        print(f'[PIRE] Annee plus chere: {worst_year["year"]} ({worst_year["pct_below_40"]:.1f}%)')

        # Price range comparison
        print(f'\nFourchettes de prix:')
        for r in results_sorted:
            print(f'   {r["year"]}: {r["min_price"]:.2f}EUR -> {r["max_price"]:.2f}EUR (mediane: {r["median_price"]:.2f}EUR)')

    print('\n' + '=' * 80)

if __name__ == '__main__':
    main()
