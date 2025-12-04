"""
Script 8: Consolidation et rapport final
Consolide toutes les analyses en un rapport unique
"""
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import PROCESSED_DATA_DIR, RESULTS_DIR, PRICE_THRESHOLD

def load_analysis_results():
    """
    Charge tous les résultats d'analyse
    """
    results = {}

    # 1. Exports
    exports_file = f"{PROCESSED_DATA_DIR}/exports_analysis.csv"
    if os.path.exists(exports_file):
        print(f"📂 Chargement analyse exports...")
        results['exports'] = pd.read_csv(exports_file)
    else:
        print(f"⚠️ Fichier exports non trouvé: {exports_file}")

    # 2. Écrêtage
    curtailment_file = f"{PROCESSED_DATA_DIR}/curtailment_analysis.csv"
    if os.path.exists(curtailment_file):
        print(f"📂 Chargement analyse écrêtage...")
        results['curtailment'] = pd.read_csv(curtailment_file)
    else:
        print(f"⚠️ Fichier écrêtage non trouvé: {curtailment_file}")

    # 3. Nucléaire
    nuclear_file = f"{PROCESSED_DATA_DIR}/nuclear_analysis.csv"
    if os.path.exists(nuclear_file):
        print(f"📂 Chargement analyse nucléaire...")
        results['nuclear'] = pd.read_csv(nuclear_file)
    else:
        print(f"⚠️ Fichier nucléaire non trouvé: {nuclear_file}")

    # 4. Prix négatifs
    negative_prices_file = f"{PROCESSED_DATA_DIR}/negative_prices_analysis.csv"
    if os.path.exists(negative_prices_file):
        print(f"📂 Chargement analyse prix négatifs...")
        results['negative_prices'] = pd.read_csv(negative_prices_file)
    else:
        print(f"⚠️ Fichier prix négatifs non trouvé: {negative_prices_file}")

    return results

def create_summary_report(results):
    """
    Crée un rapport consolidé
    """
    print(f"\n{'=' * 80}")
    print("RAPPORT CONSOLIDÉ - ÉNERGIE NON UTILISÉE EN FRANCE")
    print("=" * 80)
    print(f"Seuil de prix analysé: ≤{PRICE_THRESHOLD}€/MWh")
    print(f"Période: 2022-2024")
    print(f"Date du rapport: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()

    summary_data = []

    # 1. EXPORTS
    if 'exports' in results:
        exports_df = results['exports']
        total_exports_mwh = exports_df['total_mwh_exported'].sum()
        total_hours = exports_df['total_hours'].sum()

        print(f"1. EXPORTS VERS PAYS FRONTALIERS (≤{PRICE_THRESHOLD}€/MWh)")
        print(f"   Total MWh exportés: {total_exports_mwh:,.0f} MWh")
        print(f"   Soit: {total_exports_mwh/1000:,.1f} GWh")
        print(f"   Nombre d'heures: {total_hours:,}")
        print(f"   Par pays:")
        for _, row in exports_df.iterrows():
            print(f"      • {row['country']}: {row['total_mwh_exported']:,.0f} MWh "
                  f"(prix moyen: {row['avg_price_eur_mwh']:.2f} €/MWh)")

        summary_data.append({
            'categorie': 'Exports vers pays frontaliers',
            'mwh': total_exports_mwh,
            'gwh': total_exports_mwh / 1000,
            'heures': total_hours,
            'prix_moyen': exports_df['avg_price_eur_mwh'].mean()
        })
        print()

    # 2. ÉCRÊTAGE RENOUVELABLES
    if 'curtailment' in results:
        curtailment_df = results['curtailment']
        total_curtailment_mwh = curtailment_df['total_mwh_curtailed'].sum()
        total_hours = curtailment_df['total_hours'].max()

        print(f"2. ÉCRÊTAGE RENOUVELABLES (estimation)")
        print(f"   Total MWh écrêté: {total_curtailment_mwh:,.0f} MWh")
        print(f"   Soit: {total_curtailment_mwh/1000:,.1f} GWh")
        print(f"   Nombre d'heures: {total_hours:,}")
        print(f"   Par technologie:")
        for _, row in curtailment_df.iterrows():
            print(f"      • {row['technology']}: {row['total_mwh_curtailed']:,.0f} MWh")

        summary_data.append({
            'categorie': 'Écrêtage renouvelables',
            'mwh': total_curtailment_mwh,
            'gwh': total_curtailment_mwh / 1000,
            'heures': total_hours,
            'prix_moyen': curtailment_df['avg_price_during_curtailment'].mean()
        })
        print()

    # 3. NUCLÉAIRE NON PRODUIT
    if 'nuclear' in results:
        nuclear_df = results['nuclear']
        total_nuclear_mwh = nuclear_df['total_mwh_missing'].iloc[0]
        total_hours = nuclear_df['constrained_hours'].iloc[0]

        print(f"3. NUCLÉAIRE NON PRODUIT (contraintes réseau)")
        print(f"   Total MWh non produits: {total_nuclear_mwh:,.0f} MWh")
        print(f"   Soit: {total_nuclear_mwh/1000:,.1f} GWh")
        print(f"   Nombre d'heures: {total_hours:,}")

        summary_data.append({
            'categorie': 'Nucléaire non produit',
            'mwh': total_nuclear_mwh,
            'gwh': total_nuclear_mwh / 1000,
            'heures': total_hours,
            'prix_moyen': nuclear_df['avg_price_during_constraints'].iloc[0]
        })
        print()

    # 4. PRIX NÉGATIFS (contexte)
    if 'negative_prices' in results:
        negative_df = results['negative_prices']
        total_hours_neg = negative_df['total_hours_negative'].iloc[0]

        print(f"4. PRIX NÉGATIFS (contexte)")
        print(f"   Heures à prix négatif: {total_hours_neg:,.0f}")
        print(f"   Soit {total_hours_neg/24:,.1f} jours")
        print(f"   Prix minimum: {negative_df['min_price_eur_mwh'].iloc[0]:.2f} €/MWh")
        print()

    # TOTAL GLOBAL
    print(f"{'=' * 80}")
    print("🎯 SYNTHÈSE GLOBALE")
    print("=" * 80)

    summary_df = pd.DataFrame(summary_data)
    total_mwh = summary_df['mwh'].sum()
    total_gwh = summary_df['gwh'].sum()

    print(f"\nTOTAL ÉNERGIE 'DISPONIBLE' À ≤{PRICE_THRESHOLD}€/MWh:")
    print(f"   {total_mwh:,.0f} MWh")
    print(f"   {total_gwh:,.1f} GWh")
    print(f"   {total_gwh/1000:,.2f} TWh")
    print()

    print("Répartition:")
    for _, row in summary_df.iterrows():
        pct = (row['mwh'] / total_mwh) * 100
        print(f"   • {row['categorie']}: {row['gwh']:,.1f} GWh ({pct:.1f}%)")

    print()
    print("💡 INTERPRÉTATION:")
    print(f"   Cette énergie aurait pu être disponible à ≤{PRICE_THRESHOLD}€/MWh")
    print("   au lieu d'être exportée, écrêtée, ou non produite")
    print()

    print("⚠️ NOTES MÉTHODOLOGIQUES:")
    print("   1. Exports: Données réelles ENTSO-E")
    print("   2. Écrêtage: Estimation conservative (valeurs minimales)")
    print("   3. Nucléaire: Estimation basée sur variations de production")
    print("   4. Pas de double-comptage entre catégories")
    print("   5. Période 2022-2024 (selon disponibilité des données)")

    return summary_df

def save_reports(summary_df):
    """
    Sauvegarde les rapports finaux
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # CSV
    csv_file = f"{RESULTS_DIR}/rapport_final.csv"
    summary_df.to_csv(csv_file, index=False)
    print(f"\n💾 Rapport CSV: {csv_file}")

    # Excel avec mise en forme
    excel_file = f"{RESULTS_DIR}/rapport_final.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        summary_df.to_excel(writer, sheet_name='Synthèse', index=False)

        # Ajouter les détails
        if os.path.exists(f"{PROCESSED_DATA_DIR}/exports_analysis.csv"):
            pd.read_csv(f"{PROCESSED_DATA_DIR}/exports_analysis.csv").to_excel(
                writer, sheet_name='Exports', index=False
            )

        if os.path.exists(f"{PROCESSED_DATA_DIR}/curtailment_analysis.csv"):
            pd.read_csv(f"{PROCESSED_DATA_DIR}/curtailment_analysis.csv").to_excel(
                writer, sheet_name='Écrêtage', index=False
            )

        if os.path.exists(f"{PROCESSED_DATA_DIR}/nuclear_analysis.csv"):
            pd.read_csv(f"{PROCESSED_DATA_DIR}/nuclear_analysis.csv").to_excel(
                writer, sheet_name='Nucléaire', index=False
            )

        if os.path.exists(f"{PROCESSED_DATA_DIR}/negative_prices_yearly.csv"):
            pd.read_csv(f"{PROCESSED_DATA_DIR}/negative_prices_yearly.csv").to_excel(
                writer, sheet_name='Prix négatifs', index=False
            )

    print(f"💾 Rapport Excel: {excel_file}")

    # Rapport texte
    txt_file = f"{RESULTS_DIR}/rapport_final.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RAPPORT FINAL - ÉNERGIE DISPONIBLE À ≤40€/MWh EN FRANCE\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Période analysée: 2022-2024\n\n")

        total = summary_df['gwh'].sum()
        f.write(f"TOTAL: {total:,.1f} GWh ({total/1000:.2f} TWh)\n\n")

        f.write("DÉTAIL PAR CATÉGORIE:\n")
        for _, row in summary_df.iterrows():
            f.write(f"  {row['categorie']}: {row['gwh']:,.1f} GWh\n")

    print(f"💾 Rapport texte: {txt_file}")

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("CONSOLIDATION FINALE")
    print("=" * 80)
    print()

    # Charger les résultats
    results = load_analysis_results()

    if not results:
        print("❌ Aucun résultat à consolider")
        print("   Exécutez d'abord les scripts d'analyse 4, 5, 6, 7")
        return

    # Créer le rapport
    summary_df = create_summary_report(results)

    # Sauvegarder
    save_reports(summary_df)

    print("\n" + "=" * 80)
    print("✅ CONSOLIDATION TERMINÉE!")
    print("=" * 80)
    print(f"\nRapports disponibles dans: {RESULTS_DIR}/")

if __name__ == "__main__":
    main()
