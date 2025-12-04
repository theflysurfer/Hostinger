"""
Script 3: Extraction des prix EPEX SPOT via RTE Data Portal
Récupère: prix horaires du marché français
Période: 2022-2024
"""
import requests
import pandas as pd
import sys
import os
import base64
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import (
    RTE_CLIENT_ID, RTE_CLIENT_SECRET, RTE_TOKEN_URL, RTE_API_URL,
    START_DATE, END_DATE, RAW_DATA_DIR, REQUEST_TIMEOUT
)

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

def fetch_wholesale_prices(token, start_date, end_date):
    """
    Récupère les prix wholesale du marché EPEX SPOT via RTE

    Args:
        token: Token OAuth2 RTE
        start_date: Date de début (format YYYY-MM-DD)
        end_date: Date de fin (format YYYY-MM-DD)

    Returns:
        DataFrame avec les prix horaires
    """
    print(f"📥 Téléchargement des prix EPEX SPOT...")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # L'API RTE nécessite des requêtes par jour
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    all_data = []
    current_date = start

    while current_date <= end:
        # Requête pour une journée
        params = {
            "start_date": current_date.strftime("%Y-%m-%dT00:00:00+00:00"),
            "end_date": (current_date + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00+00:00")
        }

        try:
            response = requests.get(
                f"{RTE_API_URL}/daily_auction",
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                if "daily_auction" in data:
                    all_data.extend(data["daily_auction"])

                print(f"   ⏳ Téléchargé: {current_date.strftime('%Y-%m-%d')}", end="\r")

            elif response.status_code == 401:
                print(f"\n❌ Token expiré, reconnexion nécessaire")
                return pd.DataFrame()

            current_date += timedelta(days=1)

        except requests.exceptions.RequestException as e:
            print(f"\n⚠️ Erreur pour {current_date.strftime('%Y-%m-%d')}: {e}")
            current_date += timedelta(days=1)
            continue

    print(f"\n✅ Total téléchargé: {len(all_data)} enregistrements")

    if not all_data:
        return pd.DataFrame()

    return pd.DataFrame(all_data)

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("EXTRACTION PRIX EPEX SPOT (via RTE Data Portal)")
    print("=" * 80)
    print(f"Période: {START_DATE} à {END_DATE}")
    print(f"Destination: {RAW_DATA_DIR}/")
    print()

    # Vérifier les credentials
    if not RTE_CLIENT_ID or not RTE_CLIENT_SECRET:
        print("❌ ERREUR: Credentials RTE non configurés!")
        print("   1. Inscrivez-vous sur https://data.rte-france.com")
        print("   2. Créez une application")
        print("   3. Récupérez votre Client ID et Client Secret")
        print("   4. Ajoutez-les dans le fichier .env")
        return

    # Créer le dossier de destination
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    try:
        # Obtenir le token d'accès
        print("🔑 Connexion à l'API RTE...")
        token = get_rte_access_token()
        print("✅ Token obtenu avec succès\n")

        # Télécharger les données
        df_prices = fetch_wholesale_prices(token, START_DATE, END_DATE)

        if df_prices.empty:
            print("❌ Aucune donnée récupérée")
            return

        # Sauvegarder
        output_file = f"{RAW_DATA_DIR}/rte_epex_prices.csv"
        df_prices.to_csv(output_file, index=False)
        print(f"\n💾 Données sauvegardées: {output_file}")

        # Aperçu
        print("\n📊 Aperçu des données:")
        print(f"   Lignes: {len(df_prices)}")
        print(f"   Colonnes: {list(df_prices.columns)}")

        if "value" in df_prices.columns:
            prices = pd.to_numeric(df_prices["value"], errors='coerce')
            print(f"\n   Prix min: {prices.min():.2f} €/MWh")
            print(f"   Prix max: {prices.max():.2f} €/MWh")
            print(f"   Prix moyen: {prices.mean():.2f} €/MWh")

        print("\n✅ Extraction terminée avec succès!")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()
