"""
Script 9: Analyse avec ODRE + RTE (sans ENTSO-E)
Analyse preliminaire de l'energie disponible a <=40EUR/MWh
"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR, RESULTS_DIR, PRICE_THRESHOLD

def load_odre_data():
    """Charge les donnees ODRE"""
    print("[1] Chargement donnees ODRE...")
    df = pd.read_csv(f"{RAW_DATA_DIR}/odre_eco2mix_national.csv")
    df['date_heure'] = pd.to_datetime(df['date_heure'])
    print(f"    [OK] {len(df):,} lignes")
    return df

def analyze_exports_by_period(df):
    """
    Analyse les exports pendant les periodes de prix bas
    Hypothese: prix bas = nuit + week-end + ete
    """
    print("\n[2] Analyse exports (estimation prix bas)...")

    df['hour'] = df['date_heure'].dt.hour
    df['month'] = df['date_heure'].dt.month
    df['dayofweek'] = df['date_heure'].dt.dayofweek

    # Periodes estimees a prix bas:
    # - Nuit (0h-6h)
    # - Ete (juin-aout) midi (11h-15h)
    # - Week-end

    is_night = df['hour'].between(0, 6)
    is_summer_noon = (df['month'].between(6, 8)) & (df['hour'].between(11, 15))
    is_weekend = df['dayofweek'].isin([5, 6])

    low_price_periods = is_night | is_summer_noon | is_weekend

    print(f"    Periodes estimees a prix bas: {low_price_periods.sum():,} heures")

    # Calculer exports pendant ces periodes
    pays = ['angleterre', 'espagne', 'italie', 'suisse', 'allemagne_belgique']

    results = []
    for p in pays:
        col = f'ech_comm_{p}'
        if col not in df.columns:
            continue

        # Exports = valeurs negatives
        exports = df[low_price_periods & (df[col] < 0)][col].abs()

        if len(exports) > 0:
            # Conversion MW -> MWh (donnees 15min = /4 puis *heures)
            total_mwh = exports.sum() / 4  # Donnees 15 min

            results.append({
                'pays': p,
                'total_mwh_exported': total_mwh,
                'heures': len(exports)
            })

            print(f"    {p:20s}: {total_mwh:>10,.0f} MWh")

    return pd.DataFrame(results)

def analyze_nuclear_variability(df):
    """
    Analyse la variabilite du nucleaire
    Nucleaire non produit = capacite max - production reelle
    """
    print("\n[3] Analyse nucleaire non produit...")

    if 'nucleaire' not in df.columns:
        return None

    # Capacite max observee
    max_capacity = df['nucleaire'].quantile(0.95)
    print(f"    Capacite P95: {max_capacity:,.0f} MW")

    # Periodes de sous-production (< 80% capacite)
    threshold = max_capacity * 0.80
    low_production = df[df['nucleaire'] < threshold]

    # Energie non produite
    missing_mw = max_capacity - low_production['nucleaire']
    total_mwh = missing_mw.sum() / 4  # Donnees 15min

    print(f"    Heures < 80% capacite: {len(low_production):,}")
    print(f"    Energie non produite: {total_mwh:,.0f} MWh")

    return {
        'max_capacity_mw': max_capacity,
        'hours_constrained': len(low_production),
        'total_mwh_missing': total_mwh
    }

def analyze_renewables_curtailment(df):
    """
    Estime l'ecretage des renouvelables
    Methode: identifier les baisses anormales pendant surproduction
    """
    print("\n[4] Analyse ecretage renouvelables...")

    # Surproduction = exports eleves
    if 'ech_physiques' not in df.columns:
        return None

    # Periodes d'exports massifs (>5000 MW)
    high_exports = df[df['ech_physiques'] < -5000]

    print(f"    Heures exports >5000 MW: {len(high_exports):,}")

    results = []

    for tech in ['eolien', 'solaire']:
        if tech not in df.columns:
            continue

        # Capacite normale
        normal_capacity = df[tech].quantile(0.90)

        # Production pendant exports massifs
        actual = high_exports[tech].mean()

        # Ecretage estime
        curtailment_mw = max(0, normal_capacity * 0.5 - actual)
        total_mwh = curtailment_mw * len(high_exports) / 4

        if total_mwh > 0:
            results.append({
                'technology': tech,
                'estimated_curtailment_mwh': total_mwh
            })
            print(f"    {tech.capitalize():10s}: {total_mwh:>10,.0f} MWh")

    return pd.DataFrame(results) if results else None

def create_summary_report(exports_df, nuclear_data, curtailment_df):
    """Cree le rapport de synthese"""
    print("\n[5] Generation rapport final...")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Calculer totaux
    total_exports = exports_df['total_mwh_exported'].sum() if not exports_df.empty else 0
    total_nuclear = nuclear_data['total_mwh_missing'] if nuclear_data else 0
    total_curtailment = curtailment_df['estimated_curtailment_mwh'].sum() if curtailment_df is not None and not curtailment_df.empty else 0

    print("\n" + "=" * 80)
    print("SYNTHESE - ENERGIE DISPONIBLE A <=40EUR/MWh (ESTIMATION)")
    print("=" * 80)
    print(f"\n1. Exports pendant periodes prix bas:")
    print(f"   {total_exports:>15,.0f} MWh")
    print(f"   {total_exports/1000:>15,.1f} GWh")

    print(f"\n2. Nucleaire non produit (contraintes):")
    print(f"   {total_nuclear:>15,.0f} MWh")
    print(f"   {total_nuclear/1000:>15,.1f} GWh")

    print(f"\n3. Ecretage renouvelables (estime):")
    print(f"   {total_curtailment:>15,.0f} MWh")
    print(f"   {total_curtailment/1000:>15,.1f} GWh")

    total_gwh = (total_exports + total_nuclear + total_curtailment) / 1000

    print(f"\n{'='*80}")
    print(f"TOTAL ESTIME:")
    print(f"   {total_gwh:>15,.1f} GWh")
    print(f"   {total_gwh/1000:>15,.2f} TWh")
    print(f"{'='*80}")

    print(f"\nValorisation a 40EUR/MWh:")
    print(f"   {total_gwh * 40:>15,.0f} Millions EUR")

    # Sauvegarder
    summary = {
        'categorie': ['Exports', 'Nucleaire non produit', 'Ecretage renouvelables', 'TOTAL'],
        'mwh': [total_exports, total_nuclear, total_curtailment, total_exports + total_nuclear + total_curtailment],
        'gwh': [total_exports/1000, total_nuclear/1000, total_curtailment/1000, total_gwh]
    }

    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(f"{RESULTS_DIR}/rapport_preliminaire.csv", index=False)
    print(f"\n[SAVE] Rapport: {RESULTS_DIR}/rapport_preliminaire.csv")

    # Sauvegarder details
    if not exports_df.empty:
        exports_df.to_csv(f"{RESULTS_DIR}/exports_detail.csv", index=False)
        print(f"[SAVE] Details exports: {RESULTS_DIR}/exports_detail.csv")

    return summary_df

def main():
    """Fonction principale"""
    print("=" * 80)
    print("ANALYSE PRELIMINAIRE - ENERGIE DISPONIBLE <=40EUR/MWh")
    print("=" * 80)
    print("Sources: ODRE (2022-2024)")
    print("Note: Analyse sans prix horaires complets (estimations)")
    print()

    # Charger donnees
    df = load_odre_data()

    # Analyses
    exports_df = analyze_exports_by_period(df)
    nuclear_data = analyze_nuclear_variability(df)
    curtailment_df = analyze_renewables_curtailment(df)

    # Rapport final
    summary = create_summary_report(exports_df, nuclear_data, curtailment_df)

    print("\n[OK] Analyse preliminaire terminee!")
    print("\nProchaines etapes:")
    print("  1. Obtenir token ENTSO-E pour prix horaires reels")
    print("  2. Affiner analyse avec prix day-ahead complets")
    print("  3. Creer dashboard interactif")

if __name__ == "__main__":
    main()
