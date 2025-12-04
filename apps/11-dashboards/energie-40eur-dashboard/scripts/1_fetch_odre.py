"""
Script 1: Extraction des données ODRE (Open Data Réseaux Énergies)
Récupère: production, consommation, échanges transfrontaliers
Période: 2022-2024
"""
import requests
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import (
    ODRE_BASE_URL, ODRE_DATASETS, START_DATE, END_DATE,
    RAW_DATA_DIR, REQUEST_TIMEOUT
)

def fetch_odre_data(dataset_id, start_date, end_date):
    """
    Télécharge les données depuis ODRE OpenDataSoft

    Args:
        dataset_id: Identifiant du dataset ODRE
        start_date: Date de début (format YYYY-MM-DD)
        end_date: Date de fin (format YYYY-MM-DD)

    Returns:
        DataFrame pandas avec les données
    """
    print(f"📥 Téléchargement du dataset: {dataset_id}")

    # Construction de l'URL avec filtres
    url = f"{ODRE_BASE_URL}/catalog/datasets/{dataset_id}/records"

    # Paramètres de la requête
    params = {
        "select": "*",
        "where": f"date_heure >= '{start_date}' AND date_heure <= '{end_date}'",
        "limit": 100,  # Récupération par batch
        "offset": 0,
        "timezone": "UTC"
    }

    all_records = []
    total_fetched = 0

    while True:
        try:
            response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                break

            all_records.extend(results)
            total_fetched += len(results)

            print(f"   ⏳ Téléchargés: {total_fetched} enregistrements", end="\r")

            # Vérifier s'il y a plus de données
            total_count = data.get("total_count", 0)
            if total_fetched >= total_count:
                break

            # Passer au batch suivant
            params["offset"] += params["limit"]

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Erreur lors du téléchargement: {e}")
            break

    print(f"\n✅ Total téléchargé: {total_fetched} enregistrements")

    if not all_records:
        return pd.DataFrame()

    # Convertir en DataFrame
    df = pd.DataFrame(all_records)
    return df

def extract_fields(df):
    """
    Extrait et normalise les champs du DataFrame ODRE
    """
    if df.empty:
        return df

    # Extraire les champs imbriqués
    records = []
    for _, row in df.iterrows():
        record = {}

        # Date/heure
        if "date_heure" in row:
            record["datetime"] = row["date_heure"]

        # Extraire tous les champs du dictionnaire principal
        for key, value in row.items():
            if key not in ["date_heure"]:
                record[key] = value

        records.append(record)

    return pd.DataFrame(records)

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("EXTRACTION DONNÉES ODRE - Données nationales éCO2mix")
    print("=" * 80)
    print(f"Période: {START_DATE} à {END_DATE}")
    print(f"Destination: {RAW_DATA_DIR}/")
    print()

    # Créer le dossier de destination si nécessaire
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Télécharger les données nationales
    dataset_id = ODRE_DATASETS["eco2mix_national"]
    df = fetch_odre_data(dataset_id, START_DATE, END_DATE)

    if df.empty:
        print("❌ Aucune donnée récupérée")
        return

    # Normaliser les données
    print("\n🔄 Normalisation des données...")
    df_normalized = extract_fields(df)

    # Sauvegarder en CSV
    output_file = f"{RAW_DATA_DIR}/odre_eco2mix_national.csv"
    df_normalized.to_csv(output_file, index=False)
    print(f"💾 Données sauvegardées: {output_file}")

    # Afficher un aperçu
    print("\n📊 Aperçu des données:")
    print(f"   Lignes: {len(df_normalized)}")
    print(f"   Colonnes: {len(df_normalized.columns)}")
    print(f"   Colonnes disponibles: {', '.join(df_normalized.columns[:10])}...")

    if len(df_normalized) > 0:
        print(f"\n   Première ligne:")
        print(f"   {df_normalized.iloc[0].to_dict()}")

    print("\n✅ Extraction ODRE terminée avec succès!")

if __name__ == "__main__":
    main()
