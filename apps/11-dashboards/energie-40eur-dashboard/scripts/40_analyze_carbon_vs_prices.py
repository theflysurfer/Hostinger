"""
Script 40: Carbon Intensity vs Spot Prices Analysis
Analyzes correlation between CO2 intensity and electricity prices ≤40€
Usage: python scripts/40_analyze_carbon_vs_prices.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

# Seaborn styling
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_electricity_maps_data():
    """Load Electricity Maps CO2 data"""
    csv_path = Path('data/raw/electricitymaps_france_2024_hourly.csv')

    if not csv_path.exists():
        logger.error(f"❌ File not found: {csv_path}")
        logger.info("   Please download the CSV from Electricity Maps:")
        logger.info("   1. Go to: https://app.electricitymaps.com/datasets")
        logger.info("   2. Select: France (FR), 2024, Hourly")
        logger.info("   3. Download and save to: data/raw/electricitymaps_france_2024_hourly.csv")
        sys.exit(1)

    logger.info(f"📂 Loading CO2 data from {csv_path}")

    # Try different column name variations
    df = pd.read_csv(csv_path)
    logger.info(f"   Columns found: {list(df.columns)}")

    # Parse datetime column (various possible names)
    datetime_cols = ['datetime', 'timestamp', 'date', 'time', 'dt']
    datetime_col = None
    for col in datetime_cols:
        if col in df.columns:
            datetime_col = col
            break

    if not datetime_col:
        logger.error(f"❌ No datetime column found. Available: {list(df.columns)}")
        sys.exit(1)

    df['datetime'] = pd.to_datetime(df[datetime_col])

    # Standardize column names
    rename_map = {}
    for col in df.columns:
        col_lower = col.lower().replace('_', '').replace(' ', '')
        if 'carbonintensity' in col_lower:
            rename_map[col] = 'carbon_intensity'
        elif 'lowcarbon' in col_lower or 'carbonfree' in col_lower:
            rename_map[col] = 'low_carbon_percentage'
        elif 'renewable' in col_lower:
            rename_map[col] = 'renewable_percentage'

    df = df.rename(columns=rename_map)

    logger.success(f"✅ Loaded {len(df)} hourly records")
    return df

def load_price_data():
    """Load ENTSO-E spot prices"""
    price_path = Path('data/processed/entsoe_2022_2024_prices_full.csv')

    if not price_path.exists():
        logger.error(f"❌ Price data not found: {price_path}")
        logger.info("   Run: python scripts/1_fetch_odre_direct.py")
        sys.exit(1)

    logger.info(f"📂 Loading price data from {price_path}")
    df = pd.read_csv(price_path)
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Filter to 2024 only
    df = df[df['year'] == 2024].copy()

    # Rename 'price' to 'price_eur_mwh' for consistency
    df = df.rename(columns={'price': 'price_eur_mwh'})

    logger.success(f"✅ Loaded {len(df)} price records for 2024")
    return df

def merge_datasets(co2_df, price_df):
    """Merge CO2 and price data on datetime"""
    logger.info("🔗 Merging CO2 and price datasets...")

    # Ensure both are in same timezone (UTC)
    if co2_df['datetime'].dt.tz is not None:
        co2_df['datetime'] = co2_df['datetime'].dt.tz_convert('UTC').dt.tz_localize(None)
    if price_df['datetime'].dt.tz is not None:
        price_df['datetime'] = price_df['datetime'].dt.tz_convert('UTC').dt.tz_localize(None)

    merged = pd.merge(
        price_df,
        co2_df[['datetime', 'carbon_intensity', 'low_carbon_percentage', 'renewable_percentage']],
        on='datetime',
        how='inner'
    )

    logger.success(f"✅ Merged {len(merged)} records ({len(merged)/len(price_df)*100:.1f}% match)")

    # Add price category
    merged['price_category'] = merged['price_eur_mwh'].apply(
        lambda x: '≤40€' if x <= 40 else '>40€'
    )

    return merged

def analyze_carbon_by_price(df):
    """Analyze carbon intensity by price category"""
    logger.info("\n📊 Analyzing carbon intensity by price category...")

    summary = df.groupby('price_category').agg({
        'carbon_intensity': ['mean', 'median', 'std', 'min', 'max'],
        'low_carbon_percentage': ['mean', 'median'],
        'renewable_percentage': ['mean', 'median'],
        'price_eur_mwh': 'count'
    }).round(2)

    logger.info("\n" + "="*80)
    logger.info("CARBON INTENSITY SUMMARY BY PRICE CATEGORY")
    logger.info("="*80)
    logger.info(f"\n{summary}")

    # Key insights
    low_price = df[df['price_category'] == '≤40€']
    high_price = df[df['price_category'] == '>40€']

    logger.info("\n" + "="*80)
    logger.info("KEY INSIGHTS")
    logger.info("="*80)

    logger.info(f"\n🟢 Hours at ≤40€/MWh: {len(low_price)} ({len(low_price)/len(df)*100:.1f}%)")
    logger.info(f"   Average CO2: {low_price['carbon_intensity'].mean():.1f} gCO₂eq/kWh")
    logger.info(f"   Low-carbon %: {low_price['low_carbon_percentage'].mean():.1f}%")
    logger.info(f"   Renewable %: {low_price['renewable_percentage'].mean():.1f}%")

    logger.info(f"\n🔴 Hours at >40€/MWh: {len(high_price)} ({len(high_price)/len(df)*100:.1f}%)")
    logger.info(f"   Average CO2: {high_price['carbon_intensity'].mean():.1f} gCO₂eq/kWh")
    logger.info(f"   Low-carbon %: {high_price['low_carbon_percentage'].mean():.1f}%")
    logger.info(f"   Renewable %: {high_price['renewable_percentage'].mean():.1f}%")

    # Delta
    carbon_diff = low_price['carbon_intensity'].mean() - high_price['carbon_intensity'].mean()
    logger.info(f"\n💡 CO2 difference: {carbon_diff:.1f} gCO₂eq/kWh ({'lower' if carbon_diff < 0 else 'higher'} when price ≤40€)")

    return summary

def create_visualizations(df):
    """Create visualization plots"""
    logger.info("\n📈 Creating visualizations...")

    viz_dir = Path('data/visualizations')
    viz_dir.mkdir(exist_ok=True)

    # 1. Carbon intensity by price bucket
    fig, ax = plt.subplots(figsize=(10, 6))
    df.boxplot(column='carbon_intensity', by='price_category', ax=ax)
    plt.title('Carbon Intensity Distribution by Price Category')
    plt.suptitle('')
    plt.xlabel('Price Category')
    plt.ylabel('Carbon Intensity (gCO₂eq/kWh)')
    plt.tight_layout()
    plt.savefig(viz_dir / 'carbon_intensity_by_price_bucket.png', dpi=300)
    logger.info(f"   ✅ Saved: carbon_intensity_by_price_bucket.png")
    plt.close()

    # 2. Low-carbon percentage vs price
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(df['price_eur_mwh'], df['low_carbon_percentage'],
                        c=df['carbon_intensity'], cmap='RdYlGn_r', alpha=0.5)
    plt.colorbar(scatter, label='Carbon Intensity (gCO₂eq/kWh)')
    plt.axvline(x=40, color='red', linestyle='--', label='40€/MWh threshold')
    plt.xlabel('Price (€/MWh)')
    plt.ylabel('Low-Carbon Percentage (%)')
    plt.title('Low-Carbon % vs Spot Price (colored by CO2 intensity)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(viz_dir / 'low_carbon_percentage_vs_price.png', dpi=300)
    logger.info(f"   ✅ Saved: low_carbon_percentage_vs_price.png")
    plt.close()

    # 3. Hourly carbon vs price scatter
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['green' if p <= 40 else 'red' for p in df['price_eur_mwh']]
    ax.scatter(df['price_eur_mwh'], df['carbon_intensity'], alpha=0.3, c=colors)
    plt.axvline(x=40, color='black', linestyle='--', linewidth=2, label='40€/MWh threshold')
    plt.xlabel('Price (€/MWh)')
    plt.ylabel('Carbon Intensity (gCO₂eq/kWh)')
    plt.title('Hourly Carbon Intensity vs Spot Price (2024)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(viz_dir / 'hourly_carbon_vs_price_scatter.png', dpi=300)
    logger.info(f"   ✅ Saved: hourly_carbon_vs_price_scatter.png")
    plt.close()

    # 4. Monthly trend
    df['month'] = df['datetime'].dt.to_period('M')
    monthly = df.groupby(['month', 'price_category']).agg({
        'carbon_intensity': 'mean',
        'price_eur_mwh': 'count'
    }).reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    for category in ['≤40€', '>40€']:
        data = monthly[monthly['price_category'] == category]
        ax.plot(data['month'].astype(str), data['carbon_intensity'],
               marker='o', label=category, linewidth=2)
    plt.xlabel('Month')
    plt.ylabel('Average Carbon Intensity (gCO₂eq/kWh)')
    plt.title('Monthly Average Carbon Intensity by Price Category')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(viz_dir / 'monthly_carbon_trend_by_price.png', dpi=300)
    logger.info(f"   ✅ Saved: monthly_carbon_trend_by_price.png")
    plt.close()

def save_merged_data(df):
    """Save merged dataset"""
    output_path = Path('data/processed/carbon_vs_prices_2024.csv')
    df.to_csv(output_path, index=False)
    logger.success(f"\n✅ Saved merged data: {output_path}")
    logger.info(f"   Size: {output_path.stat().st_size / (1024**2):.2f} MB")
    logger.info(f"   Rows: {len(df):,}")

def main():
    logger.info("="*80)
    logger.info("CARBON INTENSITY VS SPOT PRICES ANALYSIS")
    logger.info("="*80)

    # Load datasets
    co2_df = load_electricity_maps_data()
    price_df = load_price_data()

    # Merge
    merged_df = merge_datasets(co2_df, price_df)

    # Analyze
    summary = analyze_carbon_by_price(merged_df)

    # Visualize
    create_visualizations(merged_df)

    # Save
    save_merged_data(merged_df)

    logger.info("\n" + "="*80)
    logger.info("✅ ANALYSIS COMPLETE")
    logger.info("="*80)
    logger.info("\n📁 Output files:")
    logger.info("   - data/processed/carbon_vs_prices_2024.csv")
    logger.info("   - data/visualizations/carbon_intensity_by_price_bucket.png")
    logger.info("   - data/visualizations/low_carbon_percentage_vs_price.png")
    logger.info("   - data/visualizations/hourly_carbon_vs_price_scatter.png")
    logger.info("   - data/visualizations/monthly_carbon_trend_by_price.png")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"\n❌ Fatal error: {e}")
        sys.exit(1)
