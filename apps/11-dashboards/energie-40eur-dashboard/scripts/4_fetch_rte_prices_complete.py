"""
Script 4: Extraction COMPLÈTE des prix EPEX SPOT via RTE Data Portal
Récupère: prix horaires du marché français (2022-2024)
API: Wholesale Market v3.0 - france_power_exchanges
"""
import requests
import pandas as pd
import sys
import os
import base64
from datetime import datetime, timedelta
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import (
    RTE_CLIENT_ID, RTE_CLIENT_SECRET, RTE_TOKEN_URL,
    START_DATE, END_DATE, RAW_DATA_DIR, REQUEST_TIMEOUT
)

# Endpoint correct pour Wholesale Market v3.0
RTE_WHOLESALE_URL = "https://digital.iservices.rte-france.com/open_api/wholesale_market/v3/france_power_exchanges"

def get_rte_access_token():
    """
    Obtient un token OAuth2 pour l'API RTE
    Token valide 2 heures
    """
    if not RTE_CLIENT_ID or not RTE_CLIENT_SECRET:
        raise ValueError("Client ID et Secret RTE non configurés dans .env")

    # Encoder les credentials en base64
    credentials = f"{RTE_CLIENT_ID}:{RTE_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    try:
        response = requests.post(
            RTE_TOKEN_URL,
            headers=headers,
            data=data,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        token_data = response.json()
        return token_data["access_token"]

    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur lors de l'obtention du token RTE: {e}")

def fetch_prices_for_month(token, year, month):
    """
    Récupère les prix pour un mois donné

    Args:
        token: Token OAuth2 RTE
        year: Année (2022, 2023, 2024)
        month: Mois (1-12)

    Returns:
        DataFrame avec les prix horaires du mois
    """
    # Dates de début et fin du mois
    start = datetime(year, month, 1)

    # Dernier jour du mois
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(days=1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    params = {
        "start_date": start.strftime("%Y-%m-%dT00:00:00+01:00"),
        "end_date": end.strftime("%Y-%m-%dT23:59:59+01:00")
    }

    try:
        response = requests.get(
            RTE_WHOLESALE_URL,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 200:
            data = response.json()

            # L'API RTE retourne les données dans "france_power_exchanges"
            if "france_power_exchanges" in data and data["france_power_exchanges"]:
                records = []
                for entry in data["france_power_exchanges"]:
                    # Extraire les données pertinentes
                    record = {
                        "datetime": entry.get("start_date"),
                        "market_type": entry.get("market_type"),
                        "value": entry.get("value"),
                        "unit": entry.get("unit", "EUR/MWh")
                    }
                    records.append(record)

                return pd.DataFrame(records)

        elif response.status_code == 401:
            print(f"[!] Token expire, reconnexion necessaire")
            return None

        else:
            print(f"[!] Erreur HTTP {response.status_code} pour {year}-{month:02d}")
            return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        print(f"[!] Erreur pour {year}-{month:02d}: {e}")
        return pd.DataFrame()

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("EXTRACTION COMPLETE PRIX EPEX SPOT (via RTE Wholesale Market v3.0)")
    print("=" * 80)
    print(f"Periode: {START_DATE} a {END_DATE}")
    print(f"Destination: {RAW_DATA_DIR}/")
    print()

    # Vérifier les credentials
    if not RTE_CLIENT_ID or not RTE_CLIENT_SECRET:
        print("[X] ERREUR: Credentials RTE non configures!")
        print("   1. Inscrivez-vous sur https://data.rte-france.com")
        print("   2. Creez une application")
        print("   3. Souscrivez a 'Wholesale Market v3.0'")
        print("   4. Recuperez votre Client ID et Client Secret")
        print("   5. Ajoutez-les dans le fichier .env")
        return

    # Créer le dossier de destination
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    try:
        # Obtenir le token d'accès
        print("[>>] Connexion a l'API RTE...")
        token = get_rte_access_token()
        print("[+] Token obtenu avec succes\n")

        # Télécharger les données mois par mois
        start_year = int(START_DATE.split("-")[0])
        end_year = int(END_DATE.split("-")[0])

        all_data = []

        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                # Ne pas dépasser la date de fin
                if year == end_year and month > int(END_DATE.split("-")[1]):
                    break

                print(f"[>>] Telechargement {year}-{month:02d}...", end=" ")

                df_month = fetch_prices_for_month(token, year, month)

                if df_month is None:
                    # Token expiré, renouveler
                    print("Renouvellement token...")
                    token = get_rte_access_token()
                    df_month = fetch_prices_for_month(token, year, month)

                if not df_month.empty:
                    all_data.append(df_month)
                    print(f"[+] {len(df_month)} lignes")
                else:
                    print("[!] Aucune donnee")

                # Pause pour ne pas surcharger l'API
                time.sleep(0.5)

        if not all_data:
            print("\n[X] Aucune donnee recuperee")
            return

        # Combiner toutes les données
        df_prices = pd.concat(all_data, ignore_index=True)

        print(f"\n[+] Total recupere: {len(df_prices)} lignes")

        # Sauvegarder
        output_file = f"{RAW_DATA_DIR}/rte_epex_prices_complete.csv"
        df_prices.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n[>>] Donnees sauvegardees: {output_file}")

        # Aperçu
        print("\n[i] Apercu des donnees:")
        print(f"   Lignes: {len(df_prices)}")
        print(f"   Colonnes: {list(df_prices.columns)}")

        if "value" in df_prices.columns:
            prices = pd.to_numeric(df_prices["value"], errors='coerce').dropna()
            print(f"\n   Prix min: {prices.min():.2f} EUR/MWh")
            print(f"   Prix max: {prices.max():.2f} EUR/MWh")
            print(f"   Prix moyen: {prices.mean():.2f} EUR/MWh")

            # Prix <= 40€
            low_prices = prices[prices <= 40]
            print(f"\n   Prix <= 40 EUR/MWh: {len(low_prices)} heures ({len(low_prices)/len(prices)*100:.1f}%)")

        print("\n[+] Extraction terminee avec succes!")

    except Exception as e:
        print(f"\n[X] Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
