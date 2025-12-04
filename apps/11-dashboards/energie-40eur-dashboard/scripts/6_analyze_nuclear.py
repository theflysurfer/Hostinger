"""
Script 6: Analyse du nucléaire non produit (contraintes réseau, priorités réseau)
Objectif: Quantifier les MWh de nucléaire non produits pour raisons de contraintes
"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR, PROCESSED_DATA_DIR, PRICE_THRESHOLD

def load_generation_data():
    """
    Charge les données de production nucléaire
    """
    # ENTSO-E
    entsoe_file = f"{RAW_DATA_DIR}/entsoe_generation_france.csv"
    if os.path.exists(entsoe_file):
        print(f"📂 Chargement production ENTSO-E...")
        df = pd.read_csv(entsoe_file)
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])
        df = df.set_index('datetime')
        return df

    # ODRE
    odre_file = f"{RAW_DATA_DIR}/odre_eco2mix_national.csv"
    if os.path.exists(odre_file):
        print(f"📂 Chargement production ODRE...")
        df = pd.read_csv(odre_file)
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
        return df

    print("❌ Aucun fichier de production trouvé!")
    return None

def load_prices():
    """
    Charge les prix
    """
    entsoe_file = f"{RAW_DATA_DIR}/entsoe_prices_france.csv"
    if os.path.exists(entsoe_file):
        print(f"📂 Chargement des prix...")
        df = pd.read_csv(entsoe_file)
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])
        df['price'] = df.iloc[:, 1]
        df = df[['datetime', 'price']]
        df = df.set_index('datetime')
        return df
    return None

def estimate_nuclear_curtailment(generation_df, prices_df):
    """
    Estime le nucléaire non produit

    Méthode:
    1. Identifier la capacité nucléaire installée (max historique)
    2. Détecter les baisses significatives de production pendant prix bas
    3. Estimer l'énergie non produite

    Note: Le nucléaire français a ~60 GW installés, facteur de charge ~70%
    """
    print(f"\n🔍 Analyse du nucléaire non produit...")

    # Trouver la colonne nucléaire
    nuclear_col = None
    for col in generation_df.columns:
        col_lower = col.lower()
        if 'nuclear' in col_lower or 'nucleaire' in col_lower:
            nuclear_col = col
            break

    if not nuclear_col:
        print("⚠️ Aucune colonne de production nucléaire trouvée")
        print(f"   Colonnes disponibles: {generation_df.columns.tolist()}")
        return None

    print(f"   Colonne nucléaire: {nuclear_col}")

    # Statistiques de base
    nuclear_prod = generation_df[nuclear_col]
    max_capacity = nuclear_prod.max()
    p95_capacity = nuclear_prod.quantile(0.95)
    median_prod = nuclear_prod.median()

    print(f"   Capacité max observée: {max_capacity:.0f} MW")
    print(f"   Production P95: {p95_capacity:.0f} MW")
    print(f"   Production médiane: {median_prod:.0f} MW")

    # Merger avec les prix
    if prices_df is not None:
        merged = generation_df[[nuclear_col]].join(prices_df, how='inner')
        low_price_periods = merged[merged['price'] <= PRICE_THRESHOLD]
    else:
        print("   ⚠️ Pas de données de prix, analyse sans filtre prix")
        merged = generation_df[[nuclear_col]].copy()
        low_price_periods = merged

    # Détecter les baisses anormales
    # On considère qu'une production < 60% du P95 pendant prix bas = contrainte réseau
    threshold_production = p95_capacity * 0.60

    constrained_periods = low_price_periods[
        low_price_periods[nuclear_col] < threshold_production
    ]

    if len(constrained_periods) == 0:
        print("   ℹ️ Aucune contrainte significative détectée")
        return None

    # Estimer l'énergie non produite
    # Différence entre capacité normale (P95) et production réelle
    expected_production = p95_capacity
    actual_production = constrained_periods[nuclear_col]
    missing_production_mw = expected_production - actual_production

    # Convertir en MWh
    total_hours = len(constrained_periods)
    total_mwh_missing = missing_production_mw.sum()

    avg_missing_mw = missing_production_mw.mean()

    print(f"\n   Périodes contraintes identifiées: {total_hours} heures")
    print(f"   Production moyenne durant contraintes: {actual_production.mean():.0f} MW")
    print(f"   Manque moyen: {avg_missing_mw:.0f} MW")
    print(f"   Total MWh non produits: {total_mwh_missing:,.0f} MWh")

    if prices_df is not None:
        avg_price = constrained_periods['price'].mean()
        print(f"   Prix moyen durant contraintes: {avg_price:.2f} €/MWh")
    else:
        avg_price = None

    results = {
        'max_capacity_mw': max_capacity,
        'p95_capacity_mw': p95_capacity,
        'median_production_mw': median_prod,
        'constrained_hours': total_hours,
        'avg_production_during_constraints_mw': actual_production.mean(),
        'total_mwh_missing': total_mwh_missing,
        'avg_price_during_constraints': avg_price
    }

    return pd.DataFrame([results])

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("ANALYSE DU NUCLÉAIRE NON PRODUIT")
    print("=" * 80)
    print()
    print("⚠️ NOTE IMPORTANTE:")
    print("   Cette analyse estime le nucléaire non produit basé sur:")
    print("   - Les baisses significatives de production vs capacité normale")
    print("   - Les périodes de prix bas (contraintes réseau probables)")
    print("   - Estimation CONSERVATIVE")
    print()

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # Charger les données
    generation_df = load_generation_data()
    if generation_df is None:
        return

    prices_df = load_prices()

    # Analyser
    results_df = estimate_nuclear_curtailment(generation_df, prices_df)

    if results_df is None or results_df.empty:
        print("\n⚠️ Nucléaire non produit non quantifiable avec les données disponibles")
        return

    # Sauvegarder
    output_file = f"{PROCESSED_DATA_DIR}/nuclear_analysis.csv"
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Résultats sauvegardés: {output_file}")

    # Résumé
    print(f"\n{'=' * 80}")
    print("RÉSUMÉ NUCLÉAIRE NON PRODUIT")
    print("=" * 80)
    total_mwh = results_df['total_mwh_missing'].iloc[0]
    hours = results_df['constrained_hours'].iloc[0]

    print(f"\n🎯 TOTAL NUCLÉAIRE NON PRODUIT (ESTIMÉ):")
    print(f"   {total_mwh:,.0f} MWh")
    print(f"   Soit {total_mwh/1000:.1f} GWh")
    print(f"   Sur {hours:,} heures")
    print(f"   Soit {hours/24:.0f} jours équivalents")

    print("\n✅ Analyse terminée!")
    print("\n📝 RAPPEL: Estimation conservative basée sur les données disponibles")
    print("   Les contraintes réseau réelles peuvent être plus complexes")

if __name__ == "__main__":
    main()
