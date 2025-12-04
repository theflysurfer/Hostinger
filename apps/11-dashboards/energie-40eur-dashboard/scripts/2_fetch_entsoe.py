"""
Script 2: Extraction des données ENTSO-E
Récupère: prix day-ahead, flux physiques transfrontaliers, écrêtage
Période: 2022-2024
"""
from entsoe import EntsoePandasClient
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import (
    ENTSOE_API_TOKEN, EIC_CODES, START_DATE, END_DATE, RAW_DATA_DIR
)

def fetch_day_ahead_prices(client, country_code, start, end):
    """
    Récupère les prix day-ahead pour un pays
    """
    try:
        print(f"📥 Téléchargement prix day-ahead pour {country_code}...")
        prices = client.query_day_ahead_prices(country_code, start=start, end=end)
        return prices
    except Exception as e:
        print(f"❌ Erreur prix day-ahead {country_code}: {e}")
        return None

def fetch_crossborder_flows(client, country_from, country_to, start, end):
    """
    Récupère les flux physiques entre deux pays
    """
    try:
        print(f"📥 Téléchargement flux {country_from} → {country_to}...")
        flows = client.query_crossborder_flows(
            country_from, country_to, start=start, end=end
        )
        return flows
    except Exception as e:
        print(f"❌ Erreur flux {country_from} → {country_to}: {e}")
        return None

def fetch_generation_per_type(client, country_code, start, end):
    """
    Récupère la production par type d'énergie
    """
    try:
        print(f"📥 Téléchargement production par type pour {country_code}...")
        generation = client.query_generation(country_code, start=start, end=end)
        return generation
    except Exception as e:
        print(f"❌ Erreur production {country_code}: {e}")
        return None

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("EXTRACTION DONNÉES ENTSO-E")
    print("=" * 80)
    print(f"Période: {START_DATE} à {END_DATE}")
    print(f"Destination: {RAW_DATA_DIR}/")
    print()

    # Vérifier le token
    if not ENTSOE_API_TOKEN:
        print("❌ ERREUR: Token ENTSO-E non configuré!")
        print("   1. Inscrivez-vous sur https://transparency.entsoe.eu")
        print("   2. Envoyez un email à transparency@entsoe.eu avec 'Restful API access'")
        print("   3. Une fois reçu, ajoutez le token dans le fichier .env")
        return

    # Créer le dossier de destination
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Initialiser le client ENTSO-E
    print(f"🔑 Connexion à l'API ENTSO-E...")
    client = EntsoePandasClient(api_key=ENTSOE_API_TOKEN)

    # Convertir les dates
    start = pd.Timestamp(START_DATE, tz='Europe/Paris')
    end = pd.Timestamp(END_DATE, tz='Europe/Paris')

    # 1. PRIX DAY-AHEAD FRANCE
    print("\n" + "=" * 80)
    print("1. PRIX DAY-AHEAD FRANCE")
    print("=" * 80)
    prices_fr = fetch_day_ahead_prices(client, EIC_CODES["FR"], start, end)
    if prices_fr is not None:
        output_file = f"{RAW_DATA_DIR}/entsoe_prices_france.csv"
        prices_fr.to_csv(output_file)
        print(f"💾 Sauvegardé: {output_file}")
        print(f"   Période: {prices_fr.index.min()} à {prices_fr.index.max()}")
        print(f"   Nombre de valeurs: {len(prices_fr)}")

    # 2. FLUX TRANSFRONTALIERS DEPUIS LA FRANCE
    print("\n" + "=" * 80)
    print("2. FLUX TRANSFRONTALIERS FRANCE → VOISINS")
    print("=" * 80)

    neighbors = ["DE", "BE", "CH", "IT", "ES", "GB"]
    all_exports = {}

    for neighbor in neighbors:
        flows = fetch_crossborder_flows(
            client, EIC_CODES["FR"], EIC_CODES[neighbor], start, end
        )
        if flows is not None:
            all_exports[neighbor] = flows
            output_file = f"{RAW_DATA_DIR}/entsoe_flows_FR_to_{neighbor}.csv"
            flows.to_csv(output_file)
            print(f"💾 Sauvegardé: {output_file}")
            print(f"   Valeurs: {len(flows)}")

    # 3. PRODUCTION PAR TYPE FRANCE
    print("\n" + "=" * 80)
    print("3. PRODUCTION PAR TYPE - FRANCE")
    print("=" * 80)
    generation = fetch_generation_per_type(client, EIC_CODES["FR"], start, end)
    if generation is not None:
        output_file = f"{RAW_DATA_DIR}/entsoe_generation_france.csv"
        generation.to_csv(output_file)
        print(f"💾 Sauvegardé: {output_file}")
        print(f"   Types de production: {generation.columns.tolist()}")
        print(f"   Valeurs: {len(generation)}")

    print("\n✅ Extraction ENTSO-E terminée!")
    print("\n📝 NOTES:")
    print("   - Les données d'écrêtage ne sont pas toujours disponibles via l'API")
    print("   - Vérifier manuellement sur https://transparency.entsoe.eu si nécessaire")

if __name__ == "__main__":
    main()
