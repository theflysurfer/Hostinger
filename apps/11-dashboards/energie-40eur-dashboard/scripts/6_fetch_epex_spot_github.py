"""
Script 6: Téléchargement données EPEX SPOT via source GitHub communautaire
Source: https://ewoken.github.io/epex-spot-data/
Données: Prix horaires Day-Ahead France (2022-2024)
Format: CSV gratuit et open source
"""
import requests
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import RAW_DATA_DIR, REQUEST_TIMEOUT

# URLs des fichiers CSV EPEX SPOT
EPEX_BASE_URL = "https://ewoken.github.io/epex-spot-data/data"
YEARS = [2022, 2023, 2024]

def download_year_data(year):
    """
    Télécharge les données EPEX SPOT pour une année

    Args:
        year: Année à télécharger (2022, 2023, 2024)

    Returns:
        DataFrame avec les données de l'année
    """
    url = f"{EPEX_BASE_URL}/{year}.csv"

    print(f"[>>] Telechargement {year}...", end=" ")

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)

        if response.status_code == 200:
            # Lire le CSV depuis la réponse
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))

            print(f"[+] {len(df)} lignes")
            return df

        elif response.status_code == 404:
            print(f"[!] Donnees non disponibles (404)")
            return pd.DataFrame()

        else:
            print(f"[!] Erreur HTTP {response.status_code}")
            return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        print(f"[!] Erreur: {e}")
        return pd.DataFrame()

def main():
    """
    Fonction principale
    """
    print("=" * 80)
    print("TELECHARGEMENT PRIX EPEX SPOT (Source: GitHub ewoken)")
    print("=" * 80)
    print(f"Source: {EPEX_BASE_URL}")
    print(f"Annees: {YEARS}")
    print(f"Destination: {RAW_DATA_DIR}/")
    print()
    print("[i] Donnees fournies par la communaute open source")
    print("[i] Prix Day-Ahead horaires du marche francais")
    print()

    # Créer le dossier de destination
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    all_data = []

    # Télécharger chaque année
    for year in YEARS:
        df_year = download_year_data(year)

        if not df_year.empty:
            all_data.append(df_year)

    if not all_data:
        print("\n[X] Aucune donnee recuperee")
        return

    # Combiner toutes les années
    df_prices = pd.concat(all_data, ignore_index=True)

    print(f"\n[+] Total recupere: {len(df_prices)} lignes")

    # Sauvegarder
    output_file = f"{RAW_DATA_DIR}/epex_spot_prices_github.csv"
    df_prices.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n[>>] Donnees sauvegardees: {output_file}")

    # Aperçu
    print("\n[i] Apercu des donnees:")
    print(f"   Lignes: {len(df_prices)}")
    print(f"   Colonnes: {list(df_prices.columns)}")

    # Détecter la colonne de prix
    price_col = None
    for col in ['price', 'Price', 'value', 'Value', 'EUR/MWh']:
        if col in df_prices.columns:
            price_col = col
            break

    if price_col:
        prices = pd.to_numeric(df_prices[price_col], errors='coerce').dropna()

        if len(prices) > 0:
            print(f"\n   Colonne prix: '{price_col}'")
            print(f"   Prix min: {prices.min():.2f} EUR/MWh")
            print(f"   Prix max: {prices.max():.2f} EUR/MWh")
            print(f"   Prix moyen: {prices.mean():.2f} EUR/MWh")
            print(f"   Prix median: {prices.median():.2f} EUR/MWh")

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

    # Statistiques par année
    if 'date' in df_prices.columns or 'Date' in df_prices.columns or 'start_date' in df_prices.columns:
        date_col = next((col for col in ['date', 'Date', 'start_date', 'datetime'] if col in df_prices.columns), None)

        if date_col and price_col:
            print(f"\n   Statistiques par annee:")
            df_prices['year'] = pd.to_datetime(df_prices[date_col]).dt.year

            for year in sorted(df_prices['year'].unique()):
                year_data = df_prices[df_prices['year'] == year]
                year_prices = pd.to_numeric(year_data[price_col], errors='coerce').dropna()

                if len(year_prices) > 0:
                    low = year_prices[year_prices <= 40]
                    print(f"      {int(year)}: {len(year_data)} lignes, "
                          f"prix moyen {year_prices.mean():.2f} EUR/MWh, "
                          f"<= 40EUR: {len(low)} h ({len(low)/len(year_prices)*100:.1f}%)")

    print("\n[+] Telechargement termine avec succes!")
    print()
    print("[i] NOTES:")
    print("   - Donnees fournies par la communaute (non officielles)")
    print("   - Verifier la qualite avant utilisation en production")
    print("   - Pour donnees officielles: utiliser ENTSO-E API")

if __name__ == "__main__":
    main()
