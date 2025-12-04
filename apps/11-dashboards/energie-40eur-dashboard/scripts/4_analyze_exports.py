"""
Script 4: Analyse des exports vers pays frontaliers à ≤40€/MWh
Objectif: Quantifier les MWh exportés quand le prix était ≤40€
"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR, PROCESSED_DATA_DIR, PRICE_THRESHOLD

def load_prices():
    """
    Charge les prix depuis les données ENTSO-E ou RTE
    """
    # Essayer d'abord ENTSO-E
    entsoe_file = f"{RAW_DATA_DIR}/entsoe_prices_france.csv"
    if os.path.exists(entsoe_file):
        print(f"📂 Chargement des prix ENTSO-E...")
        df = pd.read_csv(entsoe_file)
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])  # Première colonne = datetime
        df['price'] = df.iloc[:, 1]  # Deuxième colonne = prix
        df = df[['datetime', 'price']]
        return df

    # Sinon essayer RTE
    rte_file = f"{RAW_DATA_DIR}/rte_epex_prices.csv"
    if os.path.exists(rte_file):
        print(f"📂 Chargement des prix RTE...")
        df = pd.read_csv(rte_file)
        # Adapter selon le format RTE
        return df

    print("❌ Aucun fichier de prix trouvé!")
    return None

def load_exports():
    """
    Charge tous les flux d'exports depuis ENTSO-E
    """
    exports = {}
    neighbors = ["DE", "BE", "CH", "IT", "ES", "GB"]

    for neighbor in neighbors:
        file_path = f"{RAW_DATA_DIR}/entsoe_flows_FR_to_{neighbor}.csv"
        if os.path.exists(file_path):
            print(f"📂 Chargement exports FR → {neighbor}...")
            df = pd.read_csv(file_path)
            df['datetime'] = pd.to_datetime(df.iloc[:, 0])
            df['flow_mw'] = df.iloc[:, 1]  # Flux en MW
            exports[neighbor] = df[['datetime', 'flow_mw']]

    return exports

def analyze_cheap_exports(prices_df, exports_dict, threshold=PRICE_THRESHOLD):
    """
    Analyse les exports pendant les périodes à prix ≤ threshold

    Args:
        prices_df: DataFrame avec datetime et price
        exports_dict: Dict de DataFrames avec datetime et flow_mw
        threshold: Seuil de prix en €/MWh

    Returns:
        DataFrame avec résultats par pays
    """
    results = []

    for country, exports_df in exports_dict.items():
        print(f"\n🔍 Analyse FR → {country}...")

        # Merger les prix et les exports
        merged = pd.merge(
            exports_df,
            prices_df,
            on='datetime',
            how='inner'
        )

        # Filtrer les heures où prix ≤ threshold ET exports > 0
        cheap_exports = merged[
            (merged['price'] <= threshold) & (merged['flow_mw'] > 0)
        ]

        if len(cheap_exports) == 0:
            print(f"   ⚠️ Aucun export à ≤{threshold}€/MWh")
            continue

        # Calculer l'énergie (MW × 1h = MWh pour données horaires)
        # Si données 15min, diviser par 4
        is_15min = len(merged) > len(merged['datetime'].dt.date.unique()) * 24 * 2

        if is_15min:
            energy_mwh = cheap_exports['flow_mw'].sum() / 4  # 15min → MWh
        else:
            energy_mwh = cheap_exports['flow_mw'].sum()  # Déjà en MWh

        # Statistiques
        total_hours = len(cheap_exports)
        avg_price = cheap_exports['price'].mean()
        min_price = cheap_exports['price'].min()
        avg_flow = cheap_exports['flow_mw'].mean()

        print(f"   ✅ {energy_mwh:,.0f} MWh exportés à ≤{threshold}€/MWh")
        print(f"      Heures concernées: {total_hours:,}")
        print(f"      Prix moyen: {avg_price:.2f} €/MWh")
        print(f"      Prix min: {min_price:.2f} €/MWh")
        print(f"      Flux moyen: {avg_flow:.0f} MW")

        results.append({
            'country': country,
            'total_mwh_exported': energy_mwh,
            'total_hours': total_hours,
            'avg_price_eur_mwh': avg_price,
            'min_price_eur_mwh': min_price,
            'avg_flow_mw': avg_flow,
            'price_threshold': threshold
        })

    return pd.DataFrame(results)

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print(f"ANALYSE DES EXPORTS À ≤{PRICE_THRESHOLD}€/MWh")
    print("=" * 80)
    print()

    # Créer dossier résultats
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # Charger les données
    prices_df = load_prices()
    if prices_df is None:
        return

    exports_dict = load_exports()
    if not exports_dict:
        print("❌ Aucune donnée d'export trouvée!")
        return

    # Analyser
    print(f"\n{'=' * 80}")
    print("ANALYSE PAR PAYS")
    print("=" * 80)

    results_df = analyze_cheap_exports(prices_df, exports_dict, PRICE_THRESHOLD)

    if results_df.empty:
        print("\n❌ Aucun export identifié à ce seuil de prix")
        return

    # Sauvegarder
    output_file = f"{PROCESSED_DATA_DIR}/exports_analysis.csv"
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Résultats sauvegardés: {output_file}")

    # Résumé global
    print(f"\n{'=' * 80}")
    print("RÉSUMÉ GLOBAL")
    print("=" * 80)
    total_mwh = results_df['total_mwh_exported'].sum()
    total_hours = results_df['total_hours'].sum()

    print(f"\n🎯 TOTAL MWh EXPORTÉS À ≤{PRICE_THRESHOLD}€/MWh:")
    print(f"   {total_mwh:,.0f} MWh")
    print(f"   Sur {total_hours:,} heures")
    print(f"   Soit {total_mwh/1000:.1f} GWh")
    print()
    print("Par pays:")
    for _, row in results_df.iterrows():
        print(f"   {row['country']}: {row['total_mwh_exported']:,.0f} MWh")

    print("\n✅ Analyse terminée!")

if __name__ == "__main__":
    main()
