"""
Script 7: Analyse des périodes à prix négatifs
Objectif: Quantifier les MWh disponibles pendant les prix négatifs
"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def load_prices():
    """
    Charge les prix
    """
    entsoe_file = f"{RAW_DATA_DIR}/entsoe_prices_france.csv"
    if os.path.exists(entsoe_file):
        print(f"📂 Chargement des prix ENTSO-E...")
        df = pd.read_csv(entsoe_file)
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])
        df['price'] = pd.to_numeric(df.iloc[:, 1], errors='coerce')
        df = df[['datetime', 'price']].dropna()
        return df

    rte_file = f"{RAW_DATA_DIR}/rte_epex_prices.csv"
    if os.path.exists(rte_file):
        print(f"📂 Chargement des prix RTE...")
        df = pd.read_csv(rte_file)
        return df

    print("❌ Aucun fichier de prix trouvé!")
    return None

def load_generation_data():
    """
    Charge les données de production
    """
    entsoe_file = f"{RAW_DATA_DIR}/entsoe_generation_france.csv"
    if os.path.exists(entsoe_file):
        print(f"📂 Chargement production ENTSO-E...")
        df = pd.read_csv(entsoe_file)
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])
        df = df.set_index('datetime')
        return df

    odre_file = f"{RAW_DATA_DIR}/odre_eco2mix_national.csv"
    if os.path.exists(odre_file):
        print(f"📂 Chargement production ODRE...")
        df = pd.read_csv(odre_file)
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
        return df

    return None

def analyze_negative_prices(prices_df, generation_df=None):
    """
    Analyse les périodes de prix négatifs

    Args:
        prices_df: DataFrame avec datetime et price
        generation_df: (optionnel) Production pour contexte

    Returns:
        DataFrame avec analyse des prix négatifs
    """
    print(f"\n🔍 Analyse des prix négatifs...")

    # Filtrer les prix négatifs
    negative_prices = prices_df[prices_df['price'] < 0].copy()

    if len(negative_prices) == 0:
        print("   ℹ️ Aucune période de prix négatif identifiée")
        return None

    total_hours = len(negative_prices)
    min_price = negative_prices['price'].min()
    avg_negative_price = negative_prices['price'].mean()

    print(f"   Total heures à prix négatif: {total_hours}")
    print(f"   Prix minimum: {min_price:.2f} €/MWh")
    print(f"   Prix moyen (négatif): {avg_negative_price:.2f} €/MWh")

    # Analyser par année
    negative_prices['year'] = negative_prices['datetime'].dt.year
    negative_prices['month'] = negative_prices['datetime'].dt.month

    yearly_stats = negative_prices.groupby('year').agg({
        'price': ['count', 'mean', 'min']
    }).reset_index()

    yearly_stats.columns = ['year', 'hours_negative', 'avg_price', 'min_price']

    print("\n   Par année:")
    for _, row in yearly_stats.iterrows():
        print(f"      {int(row['year'])}: {int(row['hours_negative'])} heures, "
              f"prix moyen {row['avg_price']:.2f} €/MWh")

    # Si on a les données de production, ajouter le contexte
    if generation_df is not None:
        print("\n   Contexte de production pendant prix négatifs:")

        negative_prices_indexed = negative_prices.set_index('datetime')
        merged = generation_df.join(negative_prices_indexed[['price']], how='inner')
        negative_production = merged[merged['price'] < 0]

        for col in generation_df.columns[:5]:  # Premières colonnes
            if col in negative_production.columns:
                avg_prod = negative_production[col].mean()
                print(f"      {col}: {avg_prod:.0f} MW (moyenne)")

    # Estimer l'énergie "disponible" pendant prix négatifs
    # On pourrait considérer toute la production pendant ces heures
    # comme potentiellement disponible à prix négatif

    results = {
        'total_hours_negative': total_hours,
        'total_days_equivalent': total_hours / 24,
        'min_price_eur_mwh': min_price,
        'avg_negative_price_eur_mwh': avg_negative_price,
        'years_analyzed': negative_prices['year'].nunique()
    }

    # Ajouter stats par année
    for _, row in yearly_stats.iterrows():
        year = int(row['year'])
        results[f'hours_negative_{year}'] = int(row['hours_negative'])

    return pd.DataFrame([results]), yearly_stats, negative_prices

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("ANALYSE DES PRIX NÉGATIFS")
    print("=" * 80)
    print()
    print("ℹ️ Les prix négatifs indiquent:")
    print("   - Surproduction d'électricité")
    print("   - Nécessité d'écrêtage des renouvelables")
    print("   - Opportunités d'achat à coût négatif")
    print()

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # Charger les données
    prices_df = load_prices()
    if prices_df is None:
        return

    generation_df = load_generation_data()

    # Analyser
    result = analyze_negative_prices(prices_df, generation_df)

    if result is None:
        print("\n⚠️ Aucune période de prix négatif trouvée")
        return

    results_df, yearly_stats, negative_prices_detail = result

    # Sauvegarder résumé
    output_file = f"{PROCESSED_DATA_DIR}/negative_prices_analysis.csv"
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Résultats sauvegardés: {output_file}")

    # Sauvegarder détails
    detail_file = f"{PROCESSED_DATA_DIR}/negative_prices_detail.csv"
    negative_prices_detail.to_csv(detail_file, index=False)
    print(f"💾 Détails sauvegardés: {detail_file}")

    # Sauvegarder stats annuelles
    yearly_file = f"{PROCESSED_DATA_DIR}/negative_prices_yearly.csv"
    yearly_stats.to_csv(yearly_file, index=False)
    print(f"💾 Stats annuelles: {yearly_file}")

    # Résumé
    print(f"\n{'=' * 80}")
    print("RÉSUMÉ PRIX NÉGATIFS")
    print("=" * 80)
    total_hours = results_df['total_hours_negative'].iloc[0]
    days = results_df['total_days_equivalent'].iloc[0]
    min_price = results_df['min_price_eur_mwh'].iloc[0]
    avg_price = results_df['avg_negative_price_eur_mwh'].iloc[0]

    print(f"\n🎯 PÉRIODES À PRIX NÉGATIFS:")
    print(f"   {total_hours:.0f} heures")
    print(f"   Soit {days:.1f} jours équivalents")
    print(f"   Prix minimum: {min_price:.2f} €/MWh")
    print(f"   Prix moyen (négatif): {avg_price:.2f} €/MWh")

    print("\n💡 INTERPRÉTATION:")
    print("   Pendant ces heures, l'électricité avait une valeur négative")
    print("   → Opportunité d'achat pour stockage ou consommation flexible")
    print("   → Écrêtage probable des renouvelables")
    print("   → Contraintes réseau importantes")

    print("\n✅ Analyse terminée!")

if __name__ == "__main__":
    main()
