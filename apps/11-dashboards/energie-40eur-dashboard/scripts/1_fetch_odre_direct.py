"""
Script 1 ALTERNATIF: Téléchargement direct des données ODRE (sans API)
Télécharge les fichiers CSV complets depuis data.gouv.fr
Plus rapide et sans limite d'appels API
"""
import requests
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR, START_DATE, END_DATE

# URLs de téléchargement direct des datasets ODRE
ODRE_DOWNLOAD_URLS = {
    "eco2mix_national_2022": "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-cons-def/exports/csv?where=date_heure%20%3E%3D%20%272022-01-01%27%20and%20date_heure%20%3C%20%272023-01-01%27&limit=-1&timezone=UTC",
    "eco2mix_national_2023": "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-cons-def/exports/csv?where=date_heure%20%3E%3D%20%272023-01-01%27%20and%20date_heure%20%3C%20%272024-01-01%27&limit=-1&timezone=UTC",
    "eco2mix_national_2024": "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-cons-def/exports/csv?where=date_heure%20%3E%3D%20%272024-01-01%27%20and%20date_heure%20%3C%20%272025-01-01%27&limit=-1&timezone=UTC",
}

def download_csv_file(url, description):
    """
    Télécharge un fichier CSV depuis une URL
    """
    print(f"[>>] Telechargement : {description}...")

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        # Lire directement en DataFrame
        from io import StringIO
        df = pd.read_csv(StringIO(response.text), sep=';')

        print(f"   [OK] {len(df):,} lignes telechargees")
        return df

    except Exception as e:
        print(f"   [ERREUR] {e}")
        return None

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("TELECHARGEMENT DIRECT ODRE (sans API)")
    print("=" * 80)
    print("Methode : Telechargement CSV complet par annee")
    print("Avantage : Pas de limite d'appels API, plus rapide")
    print()

    # Créer dossier
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    all_data = []

    # Telecharger chaque annee
    for key, url in ODRE_DOWNLOAD_URLS.items():
        year = key.split('_')[-1]
        df = download_csv_file(url, f"Donnees eCO2mix {year}")

        if df is not None:
            all_data.append(df)
        else:
            print(f"[WARNING] Impossible de telecharger {year}, on continue...")

    if not all_data:
        print("\n[ERREUR] Aucune donnee telechargee")
        return

    # Concatener toutes les annees
    print(f"\n[>>] Consolidation des donnees...")
    df_final = pd.concat(all_data, ignore_index=True)

    # Filtrer sur la période demandée
    if 'date_heure' in df_final.columns:
        df_final['date_heure'] = pd.to_datetime(df_final['date_heure'])
        df_final = df_final[
            (df_final['date_heure'] >= START_DATE) &
            (df_final['date_heure'] <= END_DATE)
        ]

    # Sauvegarder
    output_file = f"{RAW_DATA_DIR}/odre_eco2mix_national.csv"
    df_final.to_csv(output_file, index=False)
    print(f"\n[SAVE] Donnees sauvegardees: {output_file}")

    # Aperçu
    print("\n[INFO] Apercu des donnees:")
    print(f"   Total lignes: {len(df_final):,}")
    print(f"   Colonnes ({len(df_final.columns)}): {', '.join(df_final.columns[:10])}...")

    if 'date_heure' in df_final.columns:
        print(f"   Periode: {df_final['date_heure'].min()} -> {df_final['date_heure'].max()}")

    # Afficher les colonnes disponibles pour vérification
    print(f"\n[INFO] Colonnes disponibles:")
    for col in df_final.columns:
        print(f"      - {col}")

    print("\n[OK] Telechargement direct ODRE termine avec succes!")
    print("\n[INFO] AVANTAGES de cette methode:")
    print("   - Pas de limite 50 000 appels")
    print("   - Plus rapide (1 requete au lieu de 100+)")
    print("   - Pas de token necessaire")

if __name__ == "__main__":
    main()
