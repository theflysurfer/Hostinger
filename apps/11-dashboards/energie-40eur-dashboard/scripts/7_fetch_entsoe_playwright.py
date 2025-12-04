"""
Script 7: Extraction données ENTSO-E via Playwright (scraping web)
Source: https://newtransparency.entsoe.eu
Données: Prix Day-Ahead France (2022-2024)
Méthode: Automatisation navigateur avec Playwright
"""
import sys
import os
import time
import json
from datetime import datetime, timedelta
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.api_config import START_DATE, END_DATE, RAW_DATA_DIR

# Note: Ce script nécessite que Playwright soit installé et configuré via MCP
# Il sera exécuté par Claude avec accès à Playwright MCP

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
    Fonction principale - Instruction pour Claude/Playwright
    """
    print("=" * 80)
    print("EXTRACTION ENTSO-E via PLAYWRIGHT")
    print("=" * 80)
    print(f"Periode: {START_DATE} a {END_DATE}")
    print(f"Destination: {RAW_DATA_DIR}/")
    print()
    print("[i] Ce script doit etre execute par Claude avec acces Playwright MCP")
    print("[i] Il va naviguer sur https://newtransparency.entsoe.eu")
    print()

    # Créer le dossier de destination
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Générer la liste des dates
    dates = generate_date_range(START_DATE, END_DATE)
    print(f"[i] {len(dates)} jours a telecharger")
    print()

    print("=" * 80)
    print("INSTRUCTIONS POUR CLAUDE/PLAYWRIGHT:")
    print("=" * 80)
    print()
    print("1. Naviguer vers: https://newtransparency.entsoe.eu/dashboard")
    print()
    print("2. Pour chaque date dans la liste:")
    print("   - Accepter les cookies/terms si necessaire")
    print("   - Cliquer sur 'BZN|FR' (France)")
    print("   - Aller dans l'onglet 'Market'")
    print("   - Selectionner 'Energy Prices'")
    print("   - Selectionner la date du jour")
    print("   - Attendre le chargement des donnees")
    print("   - Extraire les prix Day-Ahead horaires")
    print("   - Sauvegarder dans un CSV")
    print()
    print("3. Format CSV attendu:")
    print("   date,hour,price_eur_mwh")
    print("   2022-01-01,00:00,89.06")
    print("   2022-01-01,01:00,78.48")
    print("   ...")
    print()
    print("4. Sauvegarder le fichier final:")
    print(f"   {RAW_DATA_DIR}/entsoe_prices_playwright_YYYY-MM-DD.csv")
    print()
    print("=" * 80)
    print()
    print("[!] ATTENTION: Cette methode est un FALLBACK")
    print("[!] Pour une solution robuste, utilisez l'API ENTSO-E avec token")
    print("[!] Email: transparency@entsoe.eu")
    print()

    # Sauvegarder la liste des dates pour référence
    dates_file = f"{RAW_DATA_DIR}/dates_to_download.txt"
    with open(dates_file, 'w') as f:
        for date in dates:
            f.write(f"{date}\n")

    print(f"[>>] Liste des dates sauvegardee: {dates_file}")
    print(f"[i] Total: {len(dates)} dates")
    print()
    print("[i] Prochaine etape: Executer avec Playwright MCP via Claude")

if __name__ == "__main__":
    main()
