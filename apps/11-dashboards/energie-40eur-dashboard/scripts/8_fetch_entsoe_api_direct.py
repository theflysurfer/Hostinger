"""
Script 8: Extraction données ENTSO-E via API directe (sans token)
Source: https://newtransparency.entsoe.eu/market/energyPrices/load
Données: Prix Day-Ahead France (2022-2024)
Méthode: Appels API POST directs
"""
import requests
import pandas as pd
import sys
import os
import time
from datetime import datetime, timedelta
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import START_DATE, END_DATE, RAW_DATA_DIR, REQUEST_TIMEOUT

# API endpoint découvert via analyse Playwright
ENTSOE_API_URL = "https://newtransparency.entsoe.eu/market/energyPrices/load"

# Code EIC pour France
FRANCE_EIC = "10YFR-RTE------C"

def fetch_prices_for_date(date_str):
    """
    Récupère les prix EPEX SPOT pour une date donnée

    Args:
        date_str: Date au format YYYY-MM-DD

    Returns:
        DataFrame avec les prix horaires
    """
    # Construire le payload pour l'API
    payload = {
        "selectedAreas": [f"BZN|{FRANCE_EIC}"],
        "selectedDate": date_str,
        "dataType": "DAY_AHEAD",
        "marketType": "WITHOUT_SEQUENCE"
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(
            ENTSOE_API_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()

            # Parser la réponse
            records = []

            # La structure exacte dépend de la réponse API
            # À ajuster selon le format réel retourné
            if 'data' in data:
                for item in data['data']:
                    record = {
                        'datetime': item.get('mtu'),
                        'price_eur_mwh': item.get('value')
                    }
                    records.append(record)

            return pd.DataFrame(records)

        elif response.status_code == 404:
            print(f"[!] Pas de donnees pour {date_str}")
            return pd.DataFrame()

        else:
            print(f"[!] Erreur HTTP {response.status_code} pour {date_str}")
            return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        print(f"[!] Erreur pour {date_str}: {e}")
        return pd.DataFrame()

def generate_date_range(start_date, end_date):
    """
    Génère une liste de dates entre start_date et end_date

    Args:
        start_date: Date de début (YYYY-MM-DD)
        end_date: Date de fin (YYYY-MM-DD)

    Returns:
        Liste de dates au format YYYY-MM-DD
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current = start

    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("EXTRACTION ENTSO-E via API DIRECTE (sans token)")
    print("=" * 80)
    print(f"Periode: {START_DATE} a {END_DATE}")
    print(f"Destination: {RAW_DATA_DIR}/")
    print(f"Endpoint: {ENTSOE_API_URL}")
    print()
    print("[i] Cette methode utilise l'API decouverte via Playwright")
    print("[i] Prix Day-Ahead horaires du marche francais")
    print()

    # Créer le dossier de destination
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Générer la liste des dates
    dates = generate_date_range(START_DATE, END_DATE)
    print(f"[i] {len(dates)} jours a telecharger")
    print()

    all_data = []
    success_count = 0

    # Télécharger jour par jour
    for i, date in enumerate(dates, 1):
        print(f"[{i}/{len(dates)}] Telechargement {date}...", end=" ")

        df_day = fetch_prices_for_date(date)

        if not df_day.empty:
            all_data.append(df_day)
            success_count += 1
            print(f"[+] {len(df_day)} lignes")
        else:
            print("[!] Echec")

        # Pause entre requêtes pour ne pas surcharger le serveur
        time.sleep(0.5)

        # Sauvegarder intermédiaire tous les 100 jours
        if i % 100 == 0 and all_data:
            print(f"\n[>>] Sauvegarde intermediaire ({success_count} jours)...")
            df_temp = pd.concat(all_data, ignore_index=True)
            temp_file = f"{RAW_DATA_DIR}/entsoe_prices_api_temp.csv"
            df_temp.to_csv(temp_file, index=False, encoding='utf-8')

    if not all_data:
        print("\n[X] Aucune donnee recuperee")
        print("\n[i] L'API pourrait necessiter une authentification")
        print("[i] Alternatives:")
        print("   1. Obtenir un token ENTSO-E API")
        print("   2. Utiliser le script GitHub (script 6)")
        return

    # Combiner toutes les données
    df_prices = pd.concat(all_data, ignore_index=True)

    print(f"\n[+] Total recupere: {len(df_prices)} lignes ({success_count} jours)")

    # Sauvegarder
    output_file = f"{RAW_DATA_DIR}/entsoe_prices_api_direct.csv"
    df_prices.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n[>>] Donnees sauvegardees: {output_file}")

    # Statistiques
    print("\n[i] Apercu des donnees:")
    print(f"   Lignes: {len(df_prices)}")
    print(f"   Colonnes: {list(df_prices.columns)}")

    if 'price_eur_mwh' in df_prices.columns:
        prices = pd.to_numeric(df_prices['price_eur_mwh'], errors='coerce').dropna()

        if len(prices) > 0:
            print(f"\n   Prix min: {prices.min():.2f} EUR/MWh")
            print(f"   Prix max: {prices.max():.2f} EUR/MWh")
            print(f"   Prix moyen: {prices.mean():.2f} EUR/MWh")

            # Prix <= 40€
            low_prices = prices[prices <= 40]
            print(f"\n   Prix <= 40 EUR/MWh:")
            print(f"      {len(low_prices)} heures ({len(low_prices)/len(prices)*100:.1f}%)")

            # Prix négatifs
            negative_prices = prices[prices < 0]
            if len(negative_prices) > 0:
                print(f"\n   Prix negatifs:")
                print(f"      {len(negative_prices)} heures ({len(negative_prices)/len(prices)*100:.1f}%)")
                print(f"      Prix minimum: {negative_prices.min():.2f} EUR/MWh")

    print("\n[+] Extraction terminee avec succes!")

if __name__ == "__main__":
    main()
