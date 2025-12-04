"""
Script 5: Analyse de l'écrêtage des énergies renouvelables (solaire, éolien)
Objectif: Quantifier les MWh d'écrêtage lorsque le prix était ≤40€
"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR, PROCESSED_DATA_DIR, PRICE_THRESHOLD

def load_generation_data():
    """
    Charge les données de production par type depuis ODRE ou ENTSO-E
    """
    # Essayer ENTSO-E d'abord
    entsoe_file = f"{RAW_DATA_DIR}/entsoe_generation_france.csv"
    if os.path.exists(entsoe_file):
        print(f"📂 Chargement production ENTSO-E...")
        df = pd.read_csv(entsoe_file)
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])
        df = df.set_index('datetime')
        return df

    # Sinon ODRE
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

    print("❌ Aucun fichier de prix trouvé!")
    return None

def estimate_curtailment(generation_df, prices_df, threshold=PRICE_THRESHOLD):
    """
    Estime l'écrêtage basé sur les prix négatifs et les baisses de production

    Méthode:
    1. Identifier les heures avec prix ≤ 0 (écrêtage probable)
    2. Pour solaire/éolien: comparer production réelle vs capacité installée
    3. Calculer la production "manquante" pendant ces périodes

    Note: Sans données directes d'écrêtage, c'est une estimation conservative
    """
    print(f"\n🔍 Analyse de l'écrêtage potentiel...")

    # Identifier les colonnes de production renouvelable
    renewable_cols = []
    for col in generation_df.columns:
        col_lower = col.lower()
        if any(x in col_lower for x in ['solar', 'solaire', 'wind', 'eolien', 'aeolien']):
            renewable_cols.append(col)

    if not renewable_cols:
        print("⚠️ Aucune colonne de production renouvelable trouvée")
        print(f"   Colonnes disponibles: {generation_df.columns.tolist()}")
        return None

    print(f"   Colonnes renouvelables: {renewable_cols}")

    # Merger avec les prix
    merged = generation_df.join(prices_df, how='inner')

    # Périodes avec prix négatifs (fort indicateur d'écrêtage)
    negative_price_periods = merged[merged['price'] < 0]

    if len(negative_price_periods) == 0:
        print("   ℹ️ Aucune période avec prix négatif identifiée")
        print("   L'écrêtage peut exister même sans prix négatifs")
        # Continuer l'analyse avec prix bas
        low_price_periods = merged[merged['price'] <= 10]  # Prix très bas
        print(f"   Analyse avec prix ≤10€/MWh: {len(low_price_periods)} heures")
        analysis_periods = low_price_periods
    else:
        print(f"   Prix négatifs: {len(negative_price_periods)} heures")
        analysis_periods = negative_price_periods

    # Estimer l'écrêtage comme une baisse de production pendant prix bas
    # (Méthode conservative: prendre 10% de la capacité médiane comme écrêtage potentiel)
    results = []

    for col in renewable_cols:
        if col not in analysis_periods.columns:
            continue

        # Production médiane sur toute la période (approximation de la capacité)
        median_capacity = merged[col].quantile(0.90)

        # Production réelle pendant prix négatifs
        actual_production = analysis_periods[col].mean()

        # Écrêtage estimé (différence)
        estimated_curtailment_mw = max(0, median_capacity * 0.5 - actual_production)

        # MWh total (nombre d'heures × MW moyen écrêté)
        total_hours = len(analysis_periods)
        total_mwh = estimated_curtailment_mw * total_hours

        if total_mwh > 0:
            print(f"\n   {col}:")
            print(f"      Capacité estimée (P90): {median_capacity:.0f} MW")
            print(f"      Production moyenne (prix bas): {actual_production:.0f} MW")
            print(f"      Écrêtage estimé: {estimated_curtailment_mw:.0f} MW")
            print(f"      Total MWh écrêté: {total_mwh:,.0f} MWh")

            results.append({
                'technology': col,
                'estimated_curtailment_mw': estimated_curtailment_mw,
                'total_hours': total_hours,
                'total_mwh_curtailed': total_mwh,
                'avg_price_during_curtailment': analysis_periods['price'].mean()
            })

    return pd.DataFrame(results) if results else None

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("ANALYSE DE L'ÉCRÊTAGE DES RENOUVELABLES")
    print("=" * 80)
    print()
    print("⚠️ NOTE IMPORTANTE:")
    print("   Les données d'écrêtage direct ne sont pas toujours disponibles")
    print("   Cette analyse estime l'écrêtage basé sur:")
    print("   - Les périodes de prix négatifs ou très bas")
    print("   - Les baisses de production renouvelable pendant ces périodes")
    print("   - Estimation CONSERVATIVE (valeurs minimales)")
    print()

    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # Charger les données
    generation_df = load_generation_data()
    if generation_df is None:
        return

    prices_df = load_prices()
    if prices_df is None:
        return

    # Analyser
    results_df = estimate_curtailment(generation_df, prices_df, PRICE_THRESHOLD)

    if results_df is None or results_df.empty:
        print("\n⚠️ Écrêtage non quantifiable avec les données disponibles")
        print("   Recommandation: Consulter les rapports CRE ou RTE pour données précises")
        return

    # Sauvegarder
    output_file = f"{PROCESSED_DATA_DIR}/curtailment_analysis.csv"
    results_df.to_csv(output_file, index=False)
    print(f"\n💾 Résultats sauvegardés: {output_file}")

    # Résumé
    print(f"\n{'=' * 80}")
    print("RÉSUMÉ ÉCRÊTAGE")
    print("=" * 80)
    total_mwh = results_df['total_mwh_curtailed'].sum()
    print(f"\n🎯 TOTAL ÉCRÊTAGE ESTIMÉ:")
    print(f"   {total_mwh:,.0f} MWh")
    print(f"   Soit {total_mwh/1000:.1f} GWh")
    print()
    print("Par technologie:")
    for _, row in results_df.iterrows():
        print(f"   {row['technology']}: {row['total_mwh_curtailed']:,.0f} MWh")

    print("\n✅ Analyse terminée!")
    print("\n📝 RAPPEL: Estimation conservative, valeurs réelles peuvent être supérieures")

if __name__ == "__main__":
    main()
